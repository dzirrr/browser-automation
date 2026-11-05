
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import traceback

# ==========================================
# 1. KONFIGURASI
# ==========================================

FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSeGXFxZN5txgl0_hIDyeyudsz334djkpxJMHZeI6JjgTIWwEA/viewform"
)

DATA = {
    "nama": "Peserta Uji Selenium",
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

WAIT_TIME = 15


# ==========================================
# 2. INISIALISASI BROWSER
# ==========================================

options = webdriver.ChromeOptions()

# Browser tetap terlihat selama pengujian
# Jangan aktifkan headless terlebih dahulu

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, WAIT_TIME)


# ==========================================
# 3. FUNGSI PENDUKUNG
# ==========================================

def get_question(title):
    """
    Mencari blok pertanyaan berdasarkan judulnya.
    """

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
    """
    Mengisi input atau textarea menggunakan Selenium.
    """

    wait.until(
        lambda d: element.is_displayed()
        and element.is_enabled()
    )

    element.clear()
    element.send_keys(value)

    actual = element.get_attribute("value")

    if actual != value:
        raise Exception(
            f"Nilai tidak berhasil dimasukkan. "
            f"Target: {value}, Aktual: {actual}"
        )


def fill_date(element, value):
    """
    Mengisi input tanggal menggunakan JavaScript.
    """

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


def fill_textarea(question_title, value):
    """
    Mengisi pertanyaan berbentuk paragraf.
    """

    question = get_question(question_title)

    textarea = question.find_element(
        By.CSS_SELECTOR,
        "textarea"
    )

    fill_element(textarea, value)

    print(f"{question_title}: berhasil diisi")


def select_radio(question_title, option):
    """
    Memilih opsi radio berdasarkan label.
    """

    question = get_question(question_title)

    radio = question.find_element(
        By.XPATH,
        f".//*[@role='radio' and @aria-label='{option}']"
    )

    wait.until(
        lambda d: radio.is_displayed()
        and radio.is_enabled()
    )

    radio.click()

    # Memastikan radio sudah dipilih
    selected = radio.get_attribute("aria-checked")

    if selected != "true":
        raise Exception(
            f"Opsi '{option}' belum berhasil dipilih."
        )

    print(f"{question_title}: {option}")


# ==========================================
# 4. PROSES OTOMATISASI
# ==========================================

tahap = "Memulai browser"

try:

    print("\nMembuka Google Form...")

    driver.get(FORM_URL)

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@role='listitem']")
        )
    )

    print("Halaman berhasil dibuka.")

    # --------------------------------------
    # Mengisi nama peserta
    # --------------------------------------

    tahap = "Mengisi nama peserta"

    print("\nMengisi nama peserta...")

    question = get_question("Nama peserta")

    name_input = question.find_element(
        By.CSS_SELECTOR,
        "input[type='text']"
    )

    fill_element(name_input, DATA["nama"])

    print("Nama:", DATA["nama"])

    # --------------------------------------
    # Mengisi tanggal kegiatan
    # --------------------------------------

    tahap = "Mengisi tanggal kegiatan"

    print("\nMengisi tanggal kegiatan...")

    question = get_question("Tanggal kegiatan")

    date_input = question.find_element(
        By.CSS_SELECTOR,
        "input[type='date']"
    )

    fill_date(date_input, DATA["tanggal"])

    # --------------------------------------
    # Mengisi uraian kegiatan
    # --------------------------------------

    tahap = "Mengisi uraian kegiatan"

    print("\nMengisi uraian kegiatan...")

    fill_textarea(
        "Uraian kegiatan",
        DATA["uraian"]
    )

    # --------------------------------------
    # Mengisi pembelajaran
    # --------------------------------------

    tahap = "Mengisi pembelajaran yang diperoleh"

    print("\nMengisi pembelajaran...")

    fill_textarea(
        "Pembelajaran yang diperoleh",
        DATA["pembelajaran"]
    )

    # --------------------------------------
    # Memilih status kehadiran
    # --------------------------------------

    tahap = "Memilih status kehadiran"

    print("\nMemilih status kehadiran...")

    select_radio(
        "Status kehadiran",
        DATA["status"]
    )

    # --------------------------------------
    # Ringkasan sebelum submit
    # --------------------------------------

    print("\n================================")
    print("SEMUA DATA BERHASIL DIISI")
    print("================================")

    print("Nama       :", DATA["nama"])
    print("Tanggal    :", DATA["tanggal"])
    print("Uraian     :", DATA["uraian"])
    print("Pembelajaran:", DATA["pembelajaran"])
    print("Status     :", DATA["status"])

    # --------------------------------------
    # Konfirmasi sebelum submit
    # --------------------------------------

    print("\nFormulir belum dikirim.")

    konfirmasi = input(
        "Ketik KIRIM untuk mengirim formulir: "
    )

    if konfirmasi.strip().upper() != "KIRIM":
        print("\nPengiriman dibatalkan.")
    else:

        tahap = "Mengirim formulir"

        submit_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@role='button']"
                "[.//span[normalize-space()='Kirim']]"
                " | //button[normalize-space()='Kirim']"
            ))
        )

        submit_button.click()

        print("\nFormulir sedang dikirim...")

        # ----------------------------------
        # Memeriksa konfirmasi pengiriman
        # ----------------------------------

        try:

            wait.until(
                EC.text_to_be_present_in_element(
                    (By.TAG_NAME, "body"),
                    "Your response has been recorded"
                )
            )

            print("\nBERHASIL!")
            print("Respons berhasil direkam oleh Google Form.")

        except TimeoutException:

            # Alternatif jika Google Form berbahasa Indonesia
            try:

                wait.until(
                    EC.text_to_be_present_in_element(
                        (By.TAG_NAME, "body"),
                        "Respons Anda telah direkam"
                    )
                )

                print("\nBERHASIL!")
                print("Respons berhasil direkam oleh Google Form.")

            except TimeoutException:

                print("\nStatus pengiriman belum dapat dipastikan.")
                print("Silakan periksa halaman browser secara manual.")

except Exception as e:

    print("\n================================")
    print("TERJADI KESALAHAN")
    print("================================")

    print("Tahap:", tahap)
    print("Jenis:", type(e).__name__)
    print("Pesan:", str(e))

    traceback.print_exc()

    # Screenshot untuk membantu diagnosis
    try:
        driver.save_screenshot("error_screenshot.png")
        print("\nScreenshot disimpan sebagai error_screenshot.png")
    except Exception:
        pass

finally:

    input(
        "\nTekan ENTER untuk menutup browser..."
    )

    driver.quit()