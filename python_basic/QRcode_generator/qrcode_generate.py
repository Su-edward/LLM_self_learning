import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer,
    RoundedModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask, RadialGradiantColorMask, SquareGradiantColorMask,
    VerticalGradiantColorMask, HorizontalGradiantColorMask, ImageColorMask)
from PIL import Image
import tempfile
from io import BytesIO

# Streamlit 應用程式標題
st.title("個性化 QR Code 生成器")

# 使用者輸入網址或文字
user_input = st.text_input("請輸入網址或文字：", "https://www.example.com")

# 拉條讓使用者調整QR Code圖片顯示大小
st.sidebar.header("QRcode顯示調整", divider='rainbow')
with st.sidebar.popover("相關調整"):
    image_size = st.slider("調整QR Code顯示大小（像素）", min_value=100, max_value=800, value=300)

    # 顏色選擇器
    fill_color = st.color_picker("選擇 QR Code 主體顏色", "#000000")
    back_color = st.color_picker("選擇 QR Code 背景顏色", "#FFFFFF")
    # 模組造型選擇
    drawer_style = st.selectbox(
        "選擇 QR Code 造型",
        ("Square", "GappedSquare", "Circle", "Rounded", "VerticalBars", "HorizontalBars")
    )
    # 漸層填色方式選擇
    gradient_style = st.selectbox(
        "選擇 QR Code 漸層樣式",
        ("Solid", "Radial", "Square", "Vertical", "Horizontal", "Image")
    )
    # 圖片 logo 選擇
    use_logo = st.checkbox("在QR Code中心加入Logo")
    logo_file = st.file_uploader("上傳 Logo 圖片", type=["png", "jpg"]) if use_logo else None

# 生成QR Code的按鈕
if st.button("生成 QR Code"):
    # 創建QR碼
    qr = qrcode.QRCode(
        version=1,  # 控制QR碼的大小，範圍是1到40
        error_correction=qrcode.constants.ERROR_CORRECT_H if use_logo else qrcode.constants.ERROR_CORRECT_L,  # 容錯率調整
        box_size=10,  # 每個方塊的像素大小
        border=4,  # 邊框寬度，通常是4
    )

    # 將使用者輸入的內容加入QR碼
    qr.add_data(user_input)
    qr.make(fit=True)

    # 根據選擇的模組造型設置
    if drawer_style == "Square":
        drawer = SquareModuleDrawer()
    elif drawer_style == "GappedSquare":
        drawer = GappedSquareModuleDrawer()
    elif drawer_style == "Circle":
        drawer = CircleModuleDrawer()
    elif drawer_style == "Rounded":
        drawer = RoundedModuleDrawer()
    elif drawer_style == "VerticalBars":
        drawer = VerticalBarsDrawer()
    elif drawer_style == "HorizontalBars":
        drawer = HorizontalBarsDrawer()

    # 根據選擇的漸層樣式設置
    if gradient_style == "Solid":
        color_mask = SolidFillColorMask(back_color=tuple(int(back_color[i:i+2], 16) for i in (1, 3, 5)),
                                        front_color=tuple(int(fill_color[i:i+2], 16) for i in (1, 3, 5)))
    elif gradient_style == "Radial":
        color_mask = RadialGradiantColorMask(center_color=(255, 0, 0), edge_color=(0, 0, 255))
    elif gradient_style == "Square":
        color_mask = SquareGradiantColorMask(center_color=(255, 0, 0), edge_color=(0, 0, 255))
    elif gradient_style == "Vertical":
        color_mask = VerticalGradiantColorMask(top_color=(255, 0, 0), bottom_color=(0, 0, 255))
    elif gradient_style == "Horizontal":
        color_mask = HorizontalGradiantColorMask(left_color=(255, 0, 0), right_color=(0, 0, 255))
    elif gradient_style == "Image" and logo_file:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(logo_file.read())
            temp_file.flush()
            color_mask = ImageColorMask(background=tuple(int(back_color[i:i+2], 16) for i in (1, 3, 5)),
                                        image=Image.open(temp_file.name))

    # 生成QR碼影像，根據使用者選擇的顏色和樣式進行調整
    img = qr.make_image(image_factory=StyledPilImage, module_drawer=drawer, color_mask=color_mask)

    # 如果選擇了 Logo 圖片，嵌入到 QR Code 中
    if use_logo and logo_file:
        logo = Image.open(logo_file).convert("RGBA")  # 确保Logo是RGBA格式
        logo = logo.resize((image_size // 4, image_size // 4))  # 调整 logo 大小
        img = img.convert("RGBA")  # 确保QR码图像也是RGBA格式
        img.paste(logo, (img.size[0] // 2 - logo.size[0] // 2, img.size[1] // 2 - logo.size[1] // 2), logo)

    # 轉換影像為字節流格式以便顯示在Streamlit中
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # 使用 PIL 讀取影像
    img = Image.open(img_buffer)

    # 調整圖片大小
    img = img.resize((image_size, image_size))

    # 在頁面顯示QR碼
    st.image(img, caption=f"生成的QR Code", use_column_width=False)

    # 提供下載功能
    img_buffer.seek(0)
    btn = st.download_button(
        label="下載 QR Code 圖片",
        data=img_buffer,
        file_name="qrcode.png",
        mime="image/png"
    )
