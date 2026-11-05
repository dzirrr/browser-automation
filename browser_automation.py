from datetime import datetime
from zoneinfo import ZoneInfo

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = ("https://docs.google.com/forms/d/e/"
       "1FAIpQLSeGXFxZN5txgl0_hIDyeyudsz334djkpxJMHZeI6JjgTIWwEA/viewform")

# Tanggal hari ini menurut WIB (aman walau server memakai UTC)
HARI_INI = datetime.now(ZoneInfo("Asia/Jakarta")).date()

# Data yang akan diisi (tambah dict baru untuk beberapa kali isi)
DATA = [
    {
        "nama": "Uji dengan github action 2",
        "tanggal": HARI_INI,
        "kegiatan": "Membuat otomasi formulir Absensi.",
        "pembelajaran": "Memahami cara mengisi formulir absensi secara otomatis.",
        "status": "Hadir",  # "Hadir" atau "Tidak hadir"
    },
]


def blok(wait, judul):
    """Cari blok pertanyaan berdasarkan teks judulnya."""
    xpath = (f"//div[@role='listitem'][.//div[@role='heading']"
             f"[contains(normalize-space(.), '{judul}')]]")
    return wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))


def isi_teks(driver, wait, judul, nilai):
    b = blok(wait, judul)
    kolom = [e for e in b.find_elements(
        By.CSS_SELECTOR, "input[type='text'], textarea") if e.is_displayed()]
    el = kolom[0]
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", el)
    wait.until(EC.element_to_be_clickable(el))
    el.click()
    el.send_keys(nilai)


def isi_tanggal(driver, wait, judul, tgl):
    b = blok(wait, judul)
    el = b.find_element(By.CSS_SELECTOR, "input[type='date']")
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", el)
    iso = tgl.strftime("%Y-%m-%d")
    # Isi format ISO langsung (tidak tergantung locale), lalu picu event
    driver.execute_script(
        """
        const el = arguments[0], val = arguments[1];
        const setter = Object.getOwnPropertyDescriptor(
            HTMLInputElement.prototype, 'value').set;
        el.focus();
        setter.call(el, val);
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        el.dispatchEvent(new Event('blur', {bubbles: true}));
        """,
        el, iso)
    if el.get_attribute("value") != iso:
        raise RuntimeError(
            "Tanggal gagal terisi: " + str(el.get_attribute("value")))


def isi_form(driver, wait, d):
    driver.get(URL)
    blok(wait, "Nama peserta")

    isi_teks(driver, wait, "Nama peserta", d["nama"])
    isi_tanggal(driver, wait, "Tanggal kegiatan", d["tanggal"])
    isi_teks(driver, wait, "Uraian kegiatan", d["kegiatan"])
    isi_teks(driver, wait, "Pembelajaran yang diperoleh", d["pembelajaran"])

    radio = driver.find_element(
        By.XPATH, f"//div[@role='radio' and @data-value='{d['status']}']")
    driver.execute_script("arguments[0].click();", radio)

    kirim = driver.find_element(
        By.XPATH,
        "//div[@role='button'][.//span[text()='Submit' or text()='Kirim']]")
    driver.execute_script("arguments[0].click();", kirim)

    wait.until(EC.url_contains("formResponse"))


def main():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--lang=en-US")

    driver = webdriver.Chrome(options=opts)
    wait = WebDriverWait(driver, 20)
    gagal = 0
    try:
        for i, d in enumerate(DATA, 1):
            try:
                isi_form(driver, wait, d)
                print(f"[{i}] OK: {d['nama']} - {d['tanggal']}")
            except Exception as e:
                gagal += 1
                driver.save_screenshot(f"error_{i}.png")
                print(f"[{i}] GAGAL: {d['nama']} -> {type(e).__name__}: {e}")
    finally:
        driver.quit()

    # Exit code non-nol agar GitHub Actions menandai run sebagai gagal
    if gagal:
        raise SystemExit(1)


if __name__ == "__main__":
    main()