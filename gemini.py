from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import google.generativeai as genai

google_api_key = "AIzaSyBdH5XPPt8hsRl37iWpdIxRe47N4mgNz7g"

# === Class AutoAI === #
class AutoAI:
    def __init__(self, driver, model="gpt-4o"):
        self.driver = driver
        self.model = model

    def ai(self, prompt, context_html):
        max_retries = 3
        retry_count = 0
        last_error = None
        last_code = None

        while retry_count < max_retries:
            full_prompt = f"""
                Bạn là trợ lý kiểm thử tự động. Viết mã Python dùng Selenium WebDriver (self.driver) để:

                - Context HTML: {context_html}
                - Yêu cầu: {prompt}
                {f'- Code trước đó: {last_code}' if last_code else ''}
                {f'- Lỗi trước đó: {last_error}. Hãy thử cách khác' if last_error else ''}

                ⚠️ Chỉ viết đoạn code thao tác với element.
                Không được dùng lại self.driver.get().
                Không được import bất kỳ thư viện nào.
                Không được in kết quả. Không giải thích.
                Mã phải dùng self.driver và By từ selenium.
                Không dùng try và except
                
                VD: 
                password_field = self.driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys("123456")
                """

            genai.configure(api_key='AIzaSyD6JXoz3D--n75o0GMCAhK7iNs6-LHsd2A')

            model = genai.GenerativeModel("gemini-2.0-flash")

            response = model.generate_content(full_prompt)
            code = response.text  # chứa mã trả về

            code = self.clean_code_block(code)

            print(f"\n--- AI Generated Code (Attempt {retry_count + 1}/{max_retries}) ---\n{code}\n--------------------------")
            try:

                exec(code, {"self": self, "By": By, "time": time})
                return True
            except Exception as e:
                last_error = str(e)
                last_code = code
                print(f"❌ Error khi thực thi code (Attempt {retry_count + 1}/{max_retries}): {e}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"🔄 Retrying... ({retry_count + 1}/{max_retries})")
                else:
                    print("❌ Đã hết số lần thử lại")
                    print("Full prompt: ", full_prompt)
                    return False

    def clean_code_block(self, code: str) -> str:
        """Loại bỏ ```python ... ``` trong nội dung GPT trả về"""
        code = code.strip()
        code = re.sub(r"^```(python)?", "", code)
        code = re.sub(r"```$", "", code)
        return code.strip()

# === Demo chạy thử === #
if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.maximize_window()

    auto = AutoAI(driver)

    driver.get("https://demo.growcrm.io/login")

    page_source = driver.page_source

    auto.ai(f"Nhập username: 'admin@gmail.com'. Lưu ý trước khi nhập phải clear text", page_source)
    auto.ai(f"Nhập password: '123456'. Lưu ý trước khi nhập phải clear text", page_source)
    auto.ai(f"Click bỏ chọn checkbox Remember me", page_source)
    auto.ai(f"Click vào nút Continue", page_source)
    time.sleep(5)
    driver.quit()
