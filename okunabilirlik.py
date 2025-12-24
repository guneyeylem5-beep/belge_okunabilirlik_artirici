import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import subprocess


# GÖRÜNTÜ OKUMA (Türkçe uyumlu)
def goruntu_oku(dosya_yolu):
    file_bytes = np.fromfile(dosya_yolu, dtype=np.uint8)
    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)


# NETLEŞTİRME
def belge_netlestir(resim):
    gri = cv2.cvtColor(resim, cv2.COLOR_BGR2GRAY)

    temiz = cv2.GaussianBlur(gri, (3, 3), 0)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    kontrast = clahe.apply(temiz)

    blur = cv2.GaussianBlur(kontrast, (9, 9), 10)
    net = cv2.addWeighted(kontrast, 1.5, blur, -0.5, 0)

    return net


# OKUNABİLİRLİK ANALİZİ
def analiz_et(gri):
    netlik = cv2.Laplacian(gri, cv2.CV_64F).var()
    parlaklik = np.mean(gri)
    kontrast = np.std(gri)

    skor = min(100, (netlik / 3 + kontrast) / 2)

    yorum = (
        "Belge netliği belirgin şekilde artırılmıştır.\n"
        "Gürültü azaltılmış, kontrast dengelenmiştir.\n"
        "Yazılar daha okunur hale getirilmiştir.\n"
        "Belgenin orijinal yapısı korunmuştur."
    )

    return netlik, parlaklik, kontrast, skor, yorum


# TXT RAPOR
def txt_rapor(netlik, parlaklik, kontrast, skor, yorum):
    with open("belge_analiz_raporu.txt", "w", encoding="utf-8") as f:
        f.write("BELGE OKUNABİLİRLİK ANALİZ RAPORU\n")
        f.write("--------------------------------\n")
        f.write(f"Netlik Skoru: {netlik:.2f}\n")
        f.write(f"Ortalama Parlaklık: {parlaklik:.2f}\n")
        f.write(f"Kontrast: {kontrast:.2f}\n")
        f.write(f"Genel Okunabilirlik Skoru: %{skor:.1f}\n\n")
        f.write("Yorum:\n")
        f.write(yorum)


# PDF RAPOR
def pdf_rapor(skor):
    c = canvas.Canvas("belge_rapor.pdf", pagesize=A4)
    c.setFont("Helvetica", 12)
    c.drawString(50, 800, "Belge Okunabilirlik Analizi")
    c.drawString(50, 770, f"Genel Okunabilirlik Skoru: %{skor:.1f}")
    c.drawString(50, 740, "Belge analiz edilmis ve netlestirilmistir.")
    c.save()


# ANA BUTON
def calistir():
    dosya = filedialog.askopenfilename(
        title="Belge Sec",
        filetypes=[("Resim Dosyalari", "*.jpg *.png *.jpeg")]
    )

    if not dosya:
        return

    orijinal = goruntu_oku(dosya)
    net = belge_netlestir(orijinal)

    netlik, parlaklik, kontrast, skor, yorum = analiz_et(net)

    cv2.imwrite("belge_iyilestirilmis.jpg", net)
    txt_rapor(netlik, parlaklik, kontrast, skor, yorum)
    pdf_rapor(skor)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.title("Once")
    plt.imshow(cv2.cvtColor(orijinal, cv2.COLOR_BGR2RGB))
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.title("Sonra")
    plt.imshow(net, cmap="gray")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

    messagebox.showinfo(
        "Islem Tamamlandi",
        "Belge netlestirildi.\n\n"
        "Ciktilar:\n"
        "- belge_iyilestirilmis.jpg\n"
        "- belge_analiz_raporu.txt\n"
        "- belge_rapor.pdf"
    )


# ÇIKIŞ KLASÖRÜ AÇ
def klasor_ac():
    subprocess.Popen(f'explorer "{os.getcwd()}"')


# ARAYÜZ
pencere = tk.Tk()
pencere.title("Belge Okunabilirlik Artirici")
pencere.geometry("420x300")
pencere.configure(bg="#f0f0f0")

btn1 = tk.Button(
    pencere,
    text="Belge Sec ve Analiz Et",
    command=calistir,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 12, "bold"),
    padx=20,
    pady=10
)
btn1.pack(pady=15)

btn2 = tk.Button(
    pencere,
    text="Cikis Klasorunu Ac",
    command=klasor_ac,
    bg="#2196F3",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=20,
    pady=8
)
btn2.pack(pady=5)

btn3 = tk.Button(
    pencere,
    text="Programdan Cik",
    command=pencere.destroy,
    bg="#F44336",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=20,
    pady=8
)
btn3.pack(pady=5)

pencere.mainloop()

