import random
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------------------------------------------------
# 數學與 Shamir 秘密分割演算法 (以有限體/質數 P 為基礎)
# ----------------------------------------------------------------------
PRIME = 2**31 - 1  # 使用梅森質數 2^31 - 1 作為模數 (Modulus)

def eval_poly(coefficients, x, p):
    """計算多項式 f(x) mod p"""
    result = 0
    for coeff in reversed(coefficients):
        result = (result * x + coeff) % p
    return result

def split_secret(secret_int, k, n, p=PRIME):
    """將秘密分割成 n 個碎片，需要任意 k 個碎片還原"""
    if k > n:
        raise ValueError("閾值 k 不能大於總碎片數 n！")
    if secret_int >= p:
        raise ValueError(f"秘密數值過大，請輸入小於 {p} 的整數。")
    
    # 隨機生成 k-1 個係數，a_0 為秘密值
    coeffs = [secret_int] + [random.randint(1, p - 1) for _ in range(k - 1)]
    
    shares = []
    for i in range(1, n + 1):
        x = i
        y = eval_poly(coeffs, x, p)
        shares.append((x, y))
    return shares

def extended_gcd(a, b):
    """擴充歐幾里得演算法，用於計算模逆元"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a, m):
    """計算 a 在 modulo m 下的逆元"""
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise Exception('不存在模逆元')
    return (x % m + m) % m

def recover_secret(shares, p=PRIME):
    """使用拉格朗日插值法（Lagrange Interpolation）從 k 個碎片還原秘密"""
    secret = 0
    k = len(shares)
    
    for i in range(k):
        xi, yi = shares[i]
        num = 1
        den = 1
        for j in range(k):
            if i != j:
                xj, _ = shares[j]
                num = (num * (-xj)) % p
                den = (den * (xi - xj)) % p
        
        lagrange_coeff = (num * mod_inverse(den, p)) % p
        secret = (secret + yi * lagrange_coeff) % p
        
    return (secret % p + p) % p


# ----------------------------------------------------------------------
# GUI 介面設計 (Tkinter - 現代簡潔風)
# ----------------------------------------------------------------------
class SecretSharingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("秘密金鑰分割與還原系統")
        self.geometry("700x580")
        self.resizable(False, False)

        # 全局變數
        self.generated_shares = []  # 儲存生成的碎片 [(x, y), ...]
        
        # 設定主題風格 (Modern Flat Design)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 色彩配置
        self.BG_COLOR = "#F4F6F9"
        self.CARD_BG = "#FFFFFF"
        self.PRIMARY_COLOR = "#2563EB"  # 質感藍
        self.ACCENT_COLOR = "#10B981"   # 質感綠
        self.TEXT_COLOR = "#1F2937"
        
        self.configure(bg=self.BG_COLOR)
        
        # 自訂 ttk 樣式
        self.style.configure("TNotebook", background=self.BG_COLOR, borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Microsoft JhengHei", 11, "bold"), padding=[20, 10], background="#E5E7EB")
        self.style.map("TNotebook.Tab", background=[("selected", self.PRIMARY_COLOR)], foreground=[("selected", "#FFFFFF")])
        
        self.style.configure("Card.TFrame", background=self.CARD_BG, borderwidth=0)
        self.style.configure("Header.TLabel", font=("Microsoft JhengHei", 14, "bold"), background=self.CARD_BG, foreground=self.PRIMARY_COLOR)
        self.style.configure("SubHeader.TLabel", font=("Microsoft JhengHei", 10), background=self.CARD_BG, foreground="#6B7280")
        self.style.configure("Regular.TLabel", font=("Microsoft JhengHei", 10), background=self.CARD_BG, foreground=self.TEXT_COLOR)

        self.create_widgets()

    def create_widgets(self):
        # 標題區
        header_frame = tk.Frame(self, bg=self.BG_COLOR)
        header_frame.pack(fill="x", padx=25, pady=(15, 5))
        
        tk.Label(header_frame, text="🔑 (k, n) 門檻式秘密金鑰管理系統", font=("Microsoft JhengHei", 16, "bold"), bg=self.BG_COLOR, fg=self.TEXT_COLOR).pack(anchor="w")
        tk.Label(header_frame, text="基於 Shamir Secret Sharing 演算法的金鑰切分與重構系統", font=("Microsoft JhengHei", 9), bg=self.BG_COLOR, fg="#6B7280").pack(anchor="w")

        # 分頁控制
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=15)

        # 建立兩個主要頁面
        self.tab_encode = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_decode = ttk.Frame(self.notebook, style="Card.TFrame")

        self.notebook.add(self.tab_encode, text=" 🔒 編碼端 (分割金鑰) ")
        self.notebook.add(self.tab_decode, text=" 🔓 解碼端 (還原金鑰) ")

        # 建構分頁內容
        self.build_encode_tab()
        self.build_decode_tab()

    # ------------------------------------------------------------------
    # 1. 編碼端介面
    # ------------------------------------------------------------------
    def build_encode_tab(self):
        frame = ttk.Frame(self.tab_encode, style="Card.TFrame", padding=20)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # 1. 輸入金鑰
        ttk.Label(frame, text="1. 輸入原始 Key (整數或數字金鑰)", style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        ttk.Label(frame, text="請輸入欲保護的秘密數值 (例：12345678)：", style="Regular.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        
        self.entry_key = ttk.Entry(frame, font=("Consolas", 11), width=35)
        self.entry_key.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        self.entry_key.insert(0, "20261015")  # 預設範例值

        # 2. 設定 (k, n)-threshold
        ttk.Label(frame, text="2. 設定 (k, n)-threshold 參數", style="Header.TLabel").grid(row=2, column=0, columnspan=2, sticky="w", pady=(15, 5))
        
        param_frame = tk.Frame(frame, bg=self.CARD_BG)
        param_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Label(param_frame, text="總碎片數 (n)：", style="Regular.TLabel").pack(side="left")
        self.spin_n = ttk.Spinbox(param_frame, from_=2, to=20, width=5, font=("Consolas", 10))
        self.spin_n.pack(side="left", padx=(0, 20))
        self.spin_n.set(5)

        ttk.Label(param_frame, text="解鎖門檻 (k)：", style="Regular.TLabel").pack(side="left")
        self.spin_k = ttk.Spinbox(param_frame, from_=2, to=20, width=5, font=("Consolas", 10))
        self.spin_k.pack(side="left")
        self.spin_k.set(3)

        # 產生按鈕
        btn_generate = tk.Button(frame, text="切分金鑰並產生碎片 ➔", font=("Microsoft JhengHei", 10, "bold"), 
                                 bg=self.PRIMARY_COLOR, fg="white", activebackground="#1D4ED8", activeforeground="white",
                                 relief="flat", cursor="hand2", padx=15, pady=6, command=self.on_split_key)
        btn_generate.grid(row=4, column=0, columnspan=2, sticky="w", pady=15)

        # 3. 顯示碎片清單
        ttk.Label(frame, text="3. 切分後的金鑰碎片 (Shares)", style="Header.TLabel").grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        # Listbox 與 Scrollbar
        list_frame = tk.Frame(frame, bg=self.CARD_BG)
        list_frame.grid(row=6, column=0, columnspan=2, sticky="nsew")

        self.list_shares = tk.Listbox(list_frame, font=("Consolas", 10), height=7, width=65, relief="solid", bd=1)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.list_shares.yview)
        self.list_shares.configure(yscrollcommand=scrollbar.set)

        self.list_shares.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def on_split_key(self):
        """處理金鑰分割事件"""
        raw_key = self.entry_key.get().strip()
        if not raw_key.isdigit():
            messagebox.showerror("輸入錯誤", "為確保演算法運算精確，請輸入純數字 Key！")
            return

        try:
            secret = int(raw_key)
            n = int(self.spin_n.get())
            k = int(self.spin_k.get())

            if k > n:
                messagebox.showwarning("參數錯誤", "門檻值 k 不能小於或等於 1，且不能大於總數 n！")
                return

            # 執行切分
            self.generated_shares = split_secret(secret, k, n)
            
            # 更新介面清單
            self.list_shares.delete(0, tk.END)
            for idx, (x, y) in enumerate(self.generated_shares, start=1):
                self.list_shares.insert(tk.END, f" 碎片 #{idx}  ➔  (x = {x}, y = {y})")

            # 同步更新解碼頁面的選項清單
            self.update_decode_checklist()
            messagebox.showinfo("成功", f"成功將 Key 切分為 {n} 片碎片！\n（解碼需至少任意 {k} 片）")

        except Exception as e:
            messagebox.showerror("錯誤", str(e))

    # ------------------------------------------------------------------
    # 2. 解碼端介面
    # ------------------------------------------------------------------
    def build_decode_tab(self):
        frame = ttk.Frame(self.tab_decode, style="Card.TFrame", padding=20)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(frame, text="1. 模擬蒐集碎片 (勾選任意 ≥ k 片碎片)", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        ttk.Label(frame, text="請選擇您目前已收集到的金鑰碎片組合：", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))

        # 可勾選的碎片區域
        self.check_canvas = tk.Canvas(frame, bg="#F9FAFB", height=140, highlightthickness=1, highlightbackground="#E5E7EB")
        self.check_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.check_canvas.yview)
        self.check_inner_frame = tk.Frame(self.check_canvas, bg="#F9FAFB")

        self.check_inner_frame.bind("<Configure>", lambda e: self.check_canvas.configure(scrollregion=self.check_canvas.bbox("all")))
        self.check_canvas.create_window((0, 0), window=self.check_inner_frame, anchor="nw")
        self.check_canvas.configure(yscrollcommand=self.check_scrollbar.set)

        self.check_canvas.pack(fill="x", expand=False)
        self.check_scrollbar.pack(fill="y")

        self.check_vars = []  # 保存 Checkbutton 的變數

        # 2. 還原按鈕
        btn_recover = tk.Button(frame, text="🔓 算回原本的 Key", font=("Microsoft JhengHei", 10, "bold"), 
                                bg=self.ACCENT_COLOR, fg="white", activebackground="#059669", activeforeground="white",
                                relief="flat", cursor="hand2", padx=15, pady=6, command=self.on_recover_key)
        btn_recover.pack(anchor="w", pady=15)

        # 3. 還原結果顯示區
        ttk.Label(frame, text="2. 還原結果", style="Header.TLabel").pack(anchor="w", pady=(5, 5))
        
        result_box = tk.Frame(frame, bg="#F3F4F6", bd=1, relief="solid")
        result_box.pack(fill="x", pady=5)

        self.lbl_result = tk.Label(result_box, text="等待還原...", font=("Consolas", 14, "bold"), bg="#F3F4F6", fg="#9CA3AF", pady=15)
        self.lbl_result.pack()

    def update_decode_checklist(self):
        """當編碼端產生新碎片後，動態更新解碼端的勾選清單"""
        for child in self.check_inner_frame.winfo_children():
            child.destroy()
            
        self.check_vars.clear()

        for idx, (x, y) in enumerate(self.generated_shares, start=1):
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(self.check_inner_frame, text=f"碎片 #{idx}: (x={x}, y={y})", variable=var,
                                 font=("Consolas", 10), bg="#F9FAFB", activebackground="#F9FAFB", anchor="w")
            chk.pack(fill="x", padx=10, pady=3, anchor="w")
            self.check_vars.append((var, (x, y)))

    def on_recover_key(self):
        """處理算回原始 Key 事件"""
        selected_shares = [share for var, share in self.check_vars if var.get()]

        if not selected_shares:
            messagebox.showwarning("提示", "請至少勾選一組碎片！")
            return

        try:
            k = int(self.spin_k.get())
            if len(selected_shares) < k:
                messagebox.showwarning("碎片不足", f"目前僅選取 {len(selected_shares)} 片碎片，此系統設定需至少 {k} 片才能還原！")
                
            recovered_key = recover_secret(selected_shares)
            
            # 顯示結果
            self.lbl_result.config(text=f"還原金鑰：{recovered_key}", fg="#059669")
            
        except Exception as e:
            messagebox.showerror("還原失敗", f"無法還原金鑰：{str(e)}")


if __name__ == "__main__":
    app = SecretSharingApp()
    app.mainloop()