import os
import time
import random
import re
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------
# Configurações
# -----------------------------
load_dotenv()

CSV_PATH = os.getenv("CSV_PATH", "./envios.csv")
PROFILE_DIR = os.getenv("WHATSAPP_PROFILE_DIR", "./whatsapp_profile")
BASE_URL = "https://web.whatsapp.com/"
MAX_WAIT_LOGIN = 90     # tempo (s) para você escanear o QR na 1ª vez
MAX_WAIT_UI = 20        # tempo (s) padrão de espera de elementos
PAUSA_ENTRE_CONTATOS = (4, 9)  # segundos (mín, máx) entre cada envio
PAUSA_DEPOIS_UPLOAD = (2, 4)   # pausa curta após anexar arquivo
PAUSA_DEPOIS_ENVIAR = (2, 4)   # pausa após enviar

# Se quiser rodar headless (não recomendado para 1º login), mude para True após logar
HEADLESS = False

# -----------------------------
# Utilitários
# -----------------------------
def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def normalizar_telefone(phone: str) -> str:
    # Mantém apenas dígitos
    digits = re.sub(r"\D", "", phone or "")
    if not digits.startswith("55"):
        # Assume Brasil se não tem DDI
        digits = "55" + digits
    return digits

def arquivo_existe(caminho: str) -> bool:
    try:
        return Path(caminho).expanduser().exists()
    except Exception:
        return False

def espera(driver, by, selector, timeout=MAX_WAIT_UI):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))

def clica_quando_clicavel(driver, by, selector, timeout=MAX_WAIT_UI):
    elem = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
    elem.click()
    return elem

# -----------------------------
# Inicialização do Chrome
# -----------------------------
def iniciar_navegador():
    options = webdriver.ChromeOptions()
    # Perfil persistente p/ manter sessão do WhatsApp
    Path(PROFILE_DIR).mkdir(parents=True, exist_ok=True)
    options.add_argument(f"--user-data-dir={Path(PROFILE_DIR).resolve()}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=pt-BR")
    if HEADLESS:
        options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1200, 900)
    return driver

# -----------------------------
# Fluxo WhatsApp
# -----------------------------
def garantir_login(driver):
    driver.get(BASE_URL)
    log("Abrindo WhatsApp Web...")

    # Sinais de que está logado: campo de busca ou lista de conversas
    try:
        # Tenta achar a barra de pesquisa (padrões de acessibilidade variam ao longo do tempo)
        # Tentamos múltiplos seletores para robustez.
        def logged_in_condition(drv):
            sels = [
                (By.XPATH, "//div[@contenteditable='true' and @role='textbox']"),
                (By.CSS_SELECTOR, "div[role='textbox'][contenteditable='true']"),
                (By.XPATH, "//div[@aria-label='Caixa de texto para pesquisa']"),
                (By.XPATH, "//span[@data-icon='search']"),
            ]
            for by, sel in sels:
                try:
                    elem = drv.find_element(by, sel)
                    if elem:
                        return True
                except NoSuchElementException:
                    continue
            # outro indicativo: botão de menu ou sidebar
            try:
                drv.find_element(By.CSS_SELECTOR, "header")
                return True
            except NoSuchElementException:
                return False

        WebDriverWait(driver, MAX_WAIT_LOGIN).until(lambda d: logged_in_condition(d))
        log("Sessão do WhatsApp pronta.")
    except TimeoutException:
        log("Tempo esgotado para login. Escaneie o QR e rode novamente.")
        driver.quit()
        sys.exit(1)

def abrir_chat_por_telefone(driver, phone_digits: str):
    # Abre chat por URL direta (mais estável do que pesquisar nome)
    chat_url = f"https://web.whatsapp.com/send?phone={phone_digits}&legacy=1"
    driver.get(chat_url)

    # Espera o campo de mensagem estar pronto (chat aberto)
    try:
        # Campo de digitação da mensagem (rodapé)
        def chat_ready(drv):
            try:
                drv.find_element(By.XPATH, "//footer//div[@contenteditable='true' and @role='textbox']")
                return True
            except NoSuchElementException:
                return False

        WebDriverWait(driver, MAX_WAIT_UI).until(lambda d: chat_ready(d))
        # Aguarda mais um pouquinho para carregamento final
        time.sleep(1.5)
        return True
    except TimeoutException:
        return False

def enviar_mensagem(driver, texto: str):
    if not texto:
        return
    try:
        caixa = espera(driver, By.XPATH, "//footer//div[@contenteditable='true' and @role='textbox']")
        caixa.click()
        caixa.send_keys(texto)
        caixa.send_keys(Keys.SHIFT, Keys.ENTER)  # garante quebra suave se necessário
        # Botão enviar (ícone de "Enviar")
        # Em algumas versões, ENTER sozinho envia. Para ser explícito, clicamos no botão.
        # Seletores candidatos:
        btn_sels = [
            (By.XPATH, "//footer//button[@aria-label='Enviar']"),
            (By.CSS_SELECTOR, "footer button[aria-label='Send']"),
            (By.XPATH, "//span[@data-icon='send']/ancestor::button"),
        ]
        for by, sel in btn_sels:
            try:
                clica_quando_clicavel(driver, by, sel, timeout=5)
                break
            except Exception:
                continue
        time.sleep(random.uniform(*PAUSA_DEPOIS_ENVIAR))
    except Exception as e:
        log(f"Aviso: falha ao enviar mensagem de texto: {e}")

def enviar_arquivo(driver, file_path: str, caption: str = None):
    try:
        # Botão de anexar (ícone de clipe)
        anexar_sels = [
            (By.XPATH, "//div[@title='Anexar' or @aria-label='Anexar']"),
            (By.XPATH, "//span[@data-icon='clip']/ancestor::div[@role='button']"),
            (By.CSS_SELECTOR, "div[aria-label='Attach']"),
        ]
        btn_anexar = None
        for by, sel in anexar_sels:
            try:
                btn_anexar = clica_quando_clicavel(driver, by, sel, timeout=8)
                break
            except Exception:
                continue

        if not btn_anexar:
            raise RuntimeError("Botão de anexar não encontrado.")

        time.sleep(0.8)

        # Input de arquivo (documento). Em versões recentes, há um único <input type='file'>
        input_sels = [
            (By.CSS_SELECTOR, "input[type='file']"),
            (By.XPATH, "//input[@type='file']"),
        ]
        input_file = None
        for by, sel in input_sels:
            try:
                input_file = espera(driver, by, sel, timeout=8)
                break
            except TimeoutException:
                continue

        if not input_file:
            raise RuntimeError("Campo de upload não encontrado.")

        input_file.send_keys(str(Path(file_path).resolve()))
        time.sleep(random.uniform(*PAUSA_DEPOIS_UPLOAD))

        # Campo de legenda (opcional; algumas versões usam o mesmo rodapé)
        if caption:
            try:
                # Modal de pré-visualização do envio (caption box)
                legenda_sels = [
                    (By.XPATH, "//div[@aria-label='Adicionar uma legenda...' or @aria-label='Adicione uma legenda...']"),
                    (By.XPATH, "//div[@contenteditable='true' and @role='textbox' and @data-tab='10']"),
                    (By.XPATH, "//div[@contenteditable='true' and @role='textbox']"),
                ]
                legenda = None
                for by, sel in legenda_sels:
                    try:
                        legenda = espera(driver, by, sel, timeout=6)
                        if legenda:
                            break
                    except TimeoutException:
                        continue
                if legenda:
                    legenda.click()
                    legenda.send_keys(caption)
                    time.sleep(0.5)
            except Exception:
                # Se não achou campo de legenda, segue sem
                pass

        # Botão Enviar no modal de anexo
        send_sels = [
            (By.XPATH, "//span[@data-icon='send']/ancestor::div[@role='button']"),
            (By.XPATH, "//div[@aria-label='Enviar' or @title='Enviar']"),
            (By.CSS_SELECTOR, "button[aria-label='Send']"),
        ]
        enviado = False
        for by, sel in send_sels:
            try:
                clica_quando_clicavel(driver, by, sel, timeout=10)
                enviado = True
                break
            except Exception:
                continue

        if not enviado:
            # fallback: Enter
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ENTER)
                enviado = True
            except Exception:
                pass

        if not enviado:
            raise RuntimeError("Não foi possível acionar o envio do arquivo.")

        time.sleep(random.uniform(*PAUSA_DEPOIS_ENVIAR))

    except Exception as e:
        raise RuntimeError(f"Falha ao enviar arquivo: {e}")

# -----------------------------
# Execução principal
# -----------------------------
def main():
    csv_path = Path(CSV_PATH).expanduser()
    if not csv_path.exists():
        log(f"CSV não encontrado: {csv_path.resolve()}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    # Espera colunas mínimas
    for col in ["phone", "file_path"]:
        if col not in df.columns:
            log(f"CSV precisa conter a coluna '{col}'. Colunas encontradas: {list(df.columns)}")
            sys.exit(1)

    driver = iniciar_navegador()
    try:
        garantir_login(driver)

        enviados_ok = 0
        falhas = []

        for idx, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            phone_raw = str(row.get("phone", "")).strip()
            file_path = str(row.get("file_path", "")).strip()
            message = str(row.get("message", "")).strip() if not pd.isna(row.get("message", "")) else ""

            phone = normalizar_telefone(phone_raw)

            log(f"({idx+1}/{len(df)}) Enviando para {name or phone_raw}...")

            if not arquivo_existe(file_path):
                msg = f"Arquivo não encontrado: {file_path}"
                log(msg)
                falhas.append((phone_raw, msg))
                continue

            # Abre chat
            ok_chat = abrir_chat_por_telefone(driver, phone)
            if not ok_chat:
                msg = "Não foi possível abrir o chat."
                log(msg)
                falhas.append((phone_raw, msg))
                continue

            # Envia arquivo + mensagem (mensagem como legenda, se possível)
            try:
                caption = message if message else None
                enviar_arquivo(driver, file_path, caption=caption)

                # Se legenda não foi possível, envia mensagem no chat
                if message:
                    # Pequena pausa e envia a mensagem também no chat (garante o texto)
                    time.sleep(1.0)
                    enviar_mensagem(driver, message)

                enviados_ok += 1
                log("✔ Enviado com sucesso.")
            except Exception as e:
                log(f"Falha no envio: {e}")
                falhas.append((phone_raw, str(e)))

            # Pausa entre contatos (reduz risco de bloqueio)
            time.sleep(random.uniform(*PAUSA_ENTRE_CONTATOS))

        log(f"Concluído. Enviados: {enviados_ok} | Falhas: {len(falhas)}")
        if falhas:
            log("Resumo de falhas:")
            for ph, reason in falhas:
                log(f"- {ph}: {reason}")

    finally:
        # Feche o navegador ao final (se preferir manter a sessão aberta, comente)
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()
