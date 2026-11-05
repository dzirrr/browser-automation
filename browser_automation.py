
import os
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# ==========================================
# 1. KONFIGURASI
# ==========================================

FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSeGXFxZN5txgl0_hIDyeyudsz334djkpxJMHZeI6JjgTIWwEA/viewform"
)

DATA = {
    "nama": "Uji Git Action 1",
    "tanggal": "2026-11-05",
    "uraian": (
        "Melakukan pengujian browser automation "
        "menggunakan Selenium dan Python."
    ),
    "pembelajaran": (
        "Memahami interaksi otomatis dengan elemen "
        "HTML pada Google Form."
    ),
    "status": "Hadir"
}

WAIT_TIME = 20


# ==========================================
# 2. INISIALISASI BROWSER
# ==========================================

def create_driver():

    options = webdriver.ChromeOptions()

    # Chrome berjalan tanpa tampilan browser
    options.add_argument("--headless=new")

    # Konfigurasi untuk lingkungan cloud
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Mengurangi pesan yang tidak diperlukan
    options.add_argument("--log-level=3")

    return webdriver.Chrome(options=options)


# ==========================================
# 3. FUNGSI PENDUKUNG
# ==========================================

def get_question(driver, wait, title):

    xpath = (
        f"//div[@role='listitem']"
        f"[.//*[normalize-space()='{title}']]"
    )

    return wait.until(
        EC.presence_of_element_located(
            (By.XPATH, xpath)
        )
    )


def fill_element(element, value):

    if not element.is_displayed() or not element.is_enabled():
        raise Exception("Elemen tidak dapat diinteraksikan.")

    element.clear()
    element.send_keys(value)

    actual = element.get_attribute("value")

    if actual != value:
        raise Exception(
            f"Nilai tidak sesuai. "
            f"Target: {value}, Aktual: {actual}"
        )


def fill_date(driver, element, value):

    driver.execute_script("""
        const el = arguments[0];
        const date = arguments[1];

        const setter = Object.getOwnPropertyDescriptor(
            HTMLInputElement.prototype,
            'value'
        ).set;

        setter.call(el, date);

        el.dispatchEvent(
            new Event('input', { bubbles: true })
        );

        el.dispatchEvent(
            new Event('change', { bubbles: true })
        );
    """, element, value)

    actual = element.get_attribute("value")

    print("Tanggal yang dimasukkan:", actual)

    if actual != value:
        raise Exception(
            f"Tanggal gagal diisi. "
            f"Target: {value}, Aktual: {actual}"
        )


def fill_textarea(driver, wait, title, value):

    question = get_question(driver, wait, title)

    textarea = question.find_element(
        By.CSS_SELECTOR,
        "textarea"
    )

    fill_element(textarea, value)

    print(f"{title}: berhasil diisi")


def select_radio(driver, wait, title, option):

    question = get_question(driver, wait, title)

    radio = question.find_element(
        By.XPATH,
        f".//*[@role='radio' and @aria-label='{option}']"
    )

    wait.until(
        lambda d: radio.is_displayed()
        and radio.is_enabled()
    )

    radio.click()

    selected = radio.get_attribute("aria-checked")

    if selected != "true":
        raise Exception(
            f"Opsi '{option}' belum berhasil dipilih."
        )

    print(f"{title}: {option}")


# ==========================================
# 4. FUNGSI PENGISIAN FORMULIR
# ==========================================

def fill_form(driver, wait):

    # --------------------------------------
    # Nama peserta
    # --------------------------------------

    print("\nMengisi nama peserta...")

    question = get_question(
        driver, wait, "Nama peserta"
    )

    name_input = question.find_element(
        By.CSS_SELECTOR,
        "input[type='text']"
    )

    fill_element(name_input, DATA["nama"])

    print("Nama:", DATA["nama"])

    # --------------------------------------
    # Tanggal kegiatan
    # --------------------------------------

    print("\nMengisi tanggal kegiatan...")

    question = get_question(
        driver, wait, "Tanggal kegiatan"
    )

    date_input = question.find_element(
        By.CSS_SELECTOR,
        "input[type='date']"
    )

    fill_date(
        driver,
        date_input,
        DATA["tanggal"]
    )

    # --------------------------------------
    # Uraian kegiatan
    # --------------------------------------

    print("\nMengisi uraian kegiatan...")

    fill_textarea(
        driver,
        wait,
        "Uraian kegiatan",
        DATA["uraian"]
    )

    # --------------------------------------
    # Pembelajaran
    # --------------------------------------

    print("\nMengisi pembelajaran...")

    fill_textarea(
        driver,
        wait,
        "Pembelajaran yang diperoleh",
        DATA["pembelajaran"]
    )

    # --------------------------------------
    # Status kehadiran
    # --------------------------------------

    print("\nMemilih status kehadiran...")

    select_radio(
        driver,
        wait,
        "Status kehadiran",
        DATA["status"]
    )

    print("\n================================")
    print("SEMUA DATA BERHASIL DIISI")
    print("================================")

    print("Nama        :", DATA["nama"])
    print("Tanggal     :", DATA["tanggal"])
    print("Uraian      :", DATA["uraian"])
    print("Pembelajaran:", DATA["pembelajaran"])
    print("Status      :", DATA["status"])


# ==========================================
# 5. FUNGSI SUBMIT
# ==========================================

def submit_form(driver, wait):

    print("\nMengirim formulir...")

    submit_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@role='button']"
            "[.//span[normalize-space()='Kirim']]"
            " | //button[normalize-space()='Kirim']"
        ))
    )

    submit_button.click()

    print("Tombol kirim berhasil diklik.")

    # Memeriksa konfirmasi pengiriman
    try:

        wait.until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"),
                "Your response has been recorded"
            )
        )

    except TimeoutException:

        try:

            wait.until(
                EC.text_to_be_present_in_element(
                    (By.TAG_NAME, "body"),
                    "Respons Anda telah direkam"
                )
            )

        except TimeoutException:

            raise Exception(
                "Konfirmasi pengiriman tidak ditemukan. "
                "Status submit belum dapat dipastikan."
            )

    print("\n================================")
    print("FORMULIR BERHASIL DIKIRIM")
    print("================================")

    return True


# ==========================================
# 6. PROGRAM UTAMA
# ==========================================

def main():

    driver = None
    tahap = "Inisialisasi browser"

    try:

        print("Memulai Selenium Cloud Test...")

        driver = create_driver()

        wait = WebDriverWait(driver, WAIT_TIME)

        # Membuka Google Form
        tahap = "Membuka Google Form"

        print("\nMembuka Google Form...")

        driver.get(FORM_URL)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='listitem']")
            )
        )

        print("Halaman berhasil dibuka.")

        # Mengisi seluruh pertanyaan
        tahap = "Mengisi formulir"

        fill_form(driver, wait)

        # Mengirim formulir
        tahap = "Mengirim formulir"

        submit_form(driver, wait)

        print("\nPROSES SELESAI DENGAN SUKSES.")

    except Exception as e:

        print("\n================================")
        print("TERJADI KESALAHAN")
        print("================================")

        print("Tahap:", tahap)
        print("Jenis:", type(e).__name__)
        print("Pesan:", str(e))

        traceback.print_exc()

        # Simpan screenshot ketika gagal
        if driver:

            try:

                os.makedirs("screenshots", exist_ok=True)

                driver.save_screenshot(
                    "screenshots/error_screenshot.png"
                )

                print(
                    "\nScreenshot disimpan: "
                    "screenshots/error_screenshot.png"
                )

            except Exception:
                pass

        # Membuat GitHub Actions menandai job sebagai gagal
        raise

    finally:

        if driver:

            driver.quit()

            print("\nBrowser ditutup.")


# ==========================================
# 7. EKSEKUSI
# ==========================================

if __name__ == "__main__":
    main()
