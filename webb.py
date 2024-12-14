import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from shiny import App, Inputs, Outputs, Session, render, ui, reactive
from pathlib import Path
import numpy as np
from shiny.types import ImgData
import re
from datagen import create_fakedata  # hàm tạo dữ liệu ảo mô phỏng lại dữ liệu chi tiêu

df = pd.read_csv(Path(__file__).parent / "chi_tieu_mau.csv")
df["Ngày"] = pd.to_datetime(df["Ngày"])
df["Tháng"] = df["Ngày"].dt.to_period("M")

users = pd.read_csv(Path(__file__).parent / 'tai_khoan_mat_khau.csv')


# lưu thông tin và cập nhật file chứa thông tin đăng nhập
def save_user(username, password, full_name, student_id):
    global users
    global df
    users_df = users
    new_user = pd.DataFrame({
        "tài khoản": [username],
        "Mật Khẩu": [password],
        "Tên Người Dùng": [full_name],
        "id": [student_id]
    })
    users_df = pd.concat([users_df, new_user])
    users_df.to_csv(Path(__file__).parent / "tai_khoan_mat_khau.csv", index=False)
    create_fakedata(student_id, full_name)
    df = pd.read_csv(Path(__file__).parent / "chi_tieu_mau.csv")
    users = pd.read_csv(Path(__file__).parent / 'tai_khoan_mat_khau.csv')


# tạo dataframe dựa trên mã sinh viên cung cấp
def check_input(s):
    specdata = df[df["Mã sinh viên"] == s].groupby("Danh Mục")["Số Tiền"].sum().reset_index()
    specdata = specdata.sort_values(by="Số Tiền", ascending=True)
    return specdata


# xử lí dữ liệu thời gian cho biểu đồ 2
def data_in_each_month(s, startdate, enddate):
    page2df = df[df["Mã sinh viên"] == s]
    page2df["Tháng_Số"] = page2df["Ngày"].dt.month
    page2df["Năm Số"] = page2df["Ngày"].dt.year
    page2df = page2df[
        (page2df["Ngày"] >= np.datetime64(startdate))
        & (page2df["Ngày"] <= np.datetime64(enddate))
        ]
    page2df = page2df.groupby(["Tháng", "Danh Mục"])["Số Tiền"].sum().unstack().reset_index()
    return page2df


# kiểm tra định dạng của mã sinh viên bằng RegEx (Regular Expression)
def check_msv(s):
    pattern = r'^B\d{2}D[A-Z]{3}\d{3}$'
    return re.fullmatch(pattern, s) is not None


# xóa tài khoản
def delete_acc(msv):
    global users
    global df
    users = users[users["id"] != msv]
    df = df[df['Mã sinh viên'] != msv]
    users.to_csv(Path(__file__).parent / "tai_khoan_mat_khau.csv", index=False)
    users = pd.read_csv(Path(__file__).parent / 'tai_khoan_mat_khau.csv')
    df.to_csv(Path(__file__).parent / 'chi_tieu_mau.csv', index=False)
    df = pd.read_csv(Path(__file__).parent / "chi_tieu_mau.csv")


# Signup UI
signup_ui = ui.page_fluid(
    ui.panel_title("Đăng Ký Tài Khoản"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h2("Sign Up"),
            ui.input_text("signup_username", "Username"),
            ui.input_password("signup_password", "Password"),
            ui.input_text('fullname', 'Họ và Tên', ),
            ui.input_text("msv", "Mã Sinh Viên", placeholder="VD : B24DCCC000"),
            ui.input_action_button("signup_btn", "Sign Up"),
            ui.input_action_button('backtologin', 'Back To Login'),
        )
    ),
)

# Login UI
login_ui = ui.page_fluid(
    ui.panel_title("Login Page"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h2("Login"),
            ui.input_text("username", "Username"),
            ui.input_password("password", "Password"),
            ui.input_action_button("login_btn", "Login"),
            ui.input_action_button('checksignup', ' SignUp'),
        ),

    ),
)

# Main App UI
app_ui = ui.page_navbar(

    ui.nav_panel(
        "Page1",
        ui.page_fluid(
            ui.layout_sidebar(
                ui.sidebar(
                    ui.h2("Phân tích chi tiêu cá nhân"),
                    ui.h3(ui.output_text("namesv")),
                    ui.h3(ui.output_text('masv')),
                    ui.output_image("logo"),

                    ui.input_action_button('logout', 'Đăng Xuất'),
                    ui.input_action_button('deleteacc', 'Xóa Tài Khoản'),
                ),
                ui.page_auto(
                    ui.h2("Biểu Đồ Chi Tiêu Theo Từng Danh Mục"),
                    ui.card(ui.output_plot("page1plot")),
                    ui.row(
                        ui.column(
                            6,
                            ui.card(
                                ui.h3("Bảng số liệu cho từng mục"),
                                ui.output_data_frame("dataframe"),
                            ),
                        ),
                        ui.column(
                            6,
                            ui.card(
                                ui.h3("Nhận xét"),
                                ui.h4(ui.card(ui.output_text("nhanxet1"))),
                                ui.h4(ui.card(ui.output_text("nhanxet2"))),
                            ),
                        ),
                    ),
                ),
            )
        ),
    ),
    ui.nav_panel(
        "Page2",
        ui.page_fillable(
            ui.layout_sidebar(
                ui.sidebar(
                    ui.h2("Phân tích chi tiêu cá nhân"),
                    ui.h3(ui.output_text("namesv1")),
                    ui.h3(ui.output_text('masv1')),
                    ui.output_image("logo1"),
                    ui.input_action_button('logout1', 'Đăng Xuất'),
                    ui.input_action_button('deleteacc1', 'Xóa Tài Khoản'),
                ),
                ui.page_auto(
                    ui.h2("Biểu Đồ Đường Dựa Trên Thời Gian Và Danh Mục"),
                    ui.input_date_range("daterange", "Chọn Ngày", start="2024-01-01", end="2024-12-31"),
                    ui.card(
                        ui.output_plot("page2plot"),
                        ui.card(
                            ui.h3("Nhận xét"),
                            ui.h4(ui.card(ui.output_text("nhanxetp2"))),
                            ui.h4(ui.card(ui.output_text("nhanxetp2_1"))),
                        ),
                    ),
                ),
            )
        ),
    ),
    ui.nav_spacer(),

)


# Server Logic
def server(input: Inputs, output: Outputs, session: Session):
    current_page = reactive.Value('login')
    ten_sv_hien_tai = reactive.Value('')
    ma_sinh_vien_hien_tai = reactive.Value('')

    # Xử lí Tạo Tài Khoản
    @reactive.Effect
    @reactive.event(input.signup_btn)
    def handle_signup():
        new_username = input.signup_username()
        new_password = input.signup_password()
        username = input.fullname()
        id_sinh_vien = input.msv()
        if new_username in users["tài khoản"].values:
            ui.notification_show("Tên người dùng đã tồn tại", type="error")
        elif not new_username or not new_password or not username or not id_sinh_vien:
            ui.notification_show("Mời nhập đủ thông tin", type="error")
        elif not check_msv(id_sinh_vien):
            ui.notification_show("Mời nhập đúng mã sinh viên", type="error")
        elif not users.loc[users['id'] == id_sinh_vien, 'id'].empty:
            ui.notification_show("Mã sinh viên đã tồn tại", type="error")
        else:
            save_user(new_username, new_password, username, id_sinh_vien)
            current_page.set("login")

            # Xử lí đăng nhập

    @reactive.Effect
    @reactive.event(input.login_btn)
    def handle_login():
        username = input.username()
        password = input.password()
        user_row = users.loc[users["tài khoản"] == username]
        if not user_row.empty:
            stored_password = user_row['Mật Khẩu'].values[0]
            ten_sv_hien_tai.set(user_row['Tên Người Dùng'].values[0])
            ma_sinh_vien_hien_tai.set(user_row['id'].values[0])
            if password == stored_password:
                current_page.set("app")
            else:
                ui.notification_show("Invalid password!", type="error")
        else:
            ui.notification_show("Invalid username!", type="error")

    # Chuyển sang trang tạo tk
    @reactive.Effect
    @reactive.event(input.checksignup)
    def navigate_to_signup():
        current_page.set("signup")

    # Chuyển sang trang đăng nhập
    @reactive.Effect
    @reactive.event(input.backtologin)
    def backtologin():
        current_page.set('login')

    @reactive.Effect
    @reactive.event(input.logout)
    def tologin():
        current_page.set('login')

    @reactive.Effect
    @reactive.event(input.logout1)
    def tologin():
        current_page.set('login')

    @reactive.Effect
    @reactive.event(input.deleteacc)
    def xoatk():
        delete_acc(ma_sinh_vien_hien_tai())
        current_page.set('login')

    @reactive.Effect
    @reactive.event(input.deleteacc1)
    def xoatk1():
        delete_acc(ma_sinh_vien_hien_tai())
        current_page.set('login')

    # xử lí khi current page thay đổi
    @output
    @render.ui
    def dynamic_ui():
        if current_page() == "login":
            return login_ui
        elif current_page() == "signup":
            return signup_ui
        elif current_page() == "app":
            return app_ui

    @output
    @render.image
    def logo():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "homepub.jpg"), "width": "200px"}
        return img

    @output
    @render.image
    def logo1():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "homepub.jpg"), "width": "200px"}
        return img

    @output
    @render.plot
    def page1plot():
        specdata = check_input(ma_sinh_vien_hien_tai())
        categories = specdata["Danh Mục"]
        values = specdata["Số Tiền"]
        # Vẽ biểu đồ tròn
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            values,
            labels=categories,
            autopct="%.1f%%",
            startangle=90,
            textprops={"fontsize": 10},
            colors=plt.cm.Paired.colors,
            pctdistance=0.8
        )
        centre_circle = plt.Circle((0, 0), 0.6, fc='white')
        ax.add_artist(centre_circle)
        return fig

    @output
    @render.data_frame
    def dataframe():

        specdata = check_input(ma_sinh_vien_hien_tai())
        tongtien = sum(list(specdata['Số Tiền']))
        per = []
        for i in range(len(list(specdata['Danh Mục']))):
            per.append(f'{(list(specdata['Số Tiền'])[i] / tongtien * 100):.1f}%')
        specdata['Percentage'] = per
        specdata.loc[len(specdata)] = ['Tổng Tiền', tongtien, '100%']
        specdata = specdata.sort_values(by='Số Tiền', ascending=False)
        specdata['Số Tiền'] = specdata['Số Tiền'].apply(lambda x: f'{int(x):,}')

        return specdata

    @output
    @render.text
    def namesv():
        return f"Tên Sinh Viên Hiện Tại: {ten_sv_hien_tai()}"

    @output
    @render.text
    def masv():
        return f'Mã Sinh Viên Hiện Tại: {ma_sinh_vien_hien_tai()}'

    @output
    @render.text
    def namesv1():
        return f"Tên Sinh Viên Hiện Tại: {ten_sv_hien_tai()}"

    @output
    @render.text
    def masv1():
        return f'Mã Sinh Viên Hiện Tại: {ma_sinh_vien_hien_tai()}'

    # nhận xét ở trang 1
    @output
    @render.text
    def nhanxet1():
        name = ma_sinh_vien_hien_tai()

        specdata = check_input(name)
        max_row = specdata.loc[specdata["Số Tiền"].idxmax()]
        max_category = max_row["Danh Mục"]
        max_value = max_row["Số Tiền"]
        total = specdata["Số Tiền"].sum()
        max_percentage = (max_value / total) * 100

        comments = (
            f"- Danh mục chi tiêu lớn nhất là *{max_category}* với tổng chi tiêu {int(max_value):,} VND "
            f"({max_percentage:.1f}% tổng chi tiêu)."
        )

        return comments

    @output
    @render.text
    def nhanxet2():
        name = ma_sinh_vien_hien_tai()
        specdata = check_input(name)
        min_row = specdata.loc[specdata["Số Tiền"].idxmin()]
        min_category = min_row["Danh Mục"]
        min_value = min_row["Số Tiền"]
        total = specdata["Số Tiền"].sum()
        min_percentage = (min_value / total) * 100

        comments = (
            f"- Danh mục chi tiêu nhỏ nhất là *{min_category}* với tổng chi tiêu {int(min_value):,} VND "
            f"({min_percentage:.1f}% tổng chi tiêu)."
        )

        return comments

    # nhận xét trang 2
    @output
    @render.text
    def nhanxetp2():
        name = ma_sinh_vien_hien_tai()
        startdate = input.daterange()[0]
        enddate = input.daterange()[1]
        monthly_data = data_in_each_month(name, startdate, enddate)
        only_cat = monthly_data.drop(columns="Tháng", errors="ignore").sum().reset_index()
        only_cat.columns = ["Danh Mục", "Tổng Số Tiền"]

        # Tìm danh mục có giá trị lớn nhất
        max_row = only_cat.loc[only_cat["Tổng Số Tiền"].idxmax()]
        max_cat = max_row["Danh Mục"]
        max_val = max_row["Tổng Số Tiền"]

        return f"- Danh mục chi tiêu lớn nhất là *{max_cat}* với tổng chi tiêu {int(max_val):,} VND "

    @output
    @render.text
    def nhanxetp2_1():
        name = ma_sinh_vien_hien_tai()
        startdate = input.daterange()[0]
        enddate = input.daterange()[1]
        monthly_data = data_in_each_month(name, startdate, enddate)
        only_cat = monthly_data.drop(columns="Tháng", errors="ignore").sum().reset_index()
        only_cat.columns = ["Danh Mục", "Tổng Số Tiền"]

        # Tìm danh mục có giá trị nhỏ nhất
        min_row = only_cat.loc[only_cat["Tổng Số Tiền"].idxmin()]
        min_cat = min_row["Danh Mục"]
        min_val = min_row["Tổng Số Tiền"]

        return f"- Danh mục chi tiêu lớn nhất là *{min_cat}* với tổng chi tiêu {int(min_val):,} VND "

    # biểu đồ trang 2
    @output
    @render.plot
    def page2plot():
        name = ma_sinh_vien_hien_tai()
        startdate = input.daterange()[0]
        enddate = input.daterange()[1]
        monthly_data = data_in_each_month(name, startdate, enddate)
        plt.figure(figsize=(10, 4))
        for category in monthly_data.columns[1:]:
            plt.plot(
                monthly_data['Tháng'].astype(str),
                monthly_data[category],
                label=category,
                marker="o"
            )

        def format_thousands(value, tick_number):
            return f"{int(value):,}"

        plt.gca().yaxis.set_major_formatter(FuncFormatter(format_thousands))
        plt.title("Chi Tiêu Theo Từng Mục Qua Các Tháng", fontsize=16)
        plt.xlabel("Tháng", fontsize=12)
        plt.ylabel("Số Tiền (VND)", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title="Danh Mục", fontsize=10, bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        return plt.gcf()


# Tạo Web
app = App(ui.output_ui("dynamic_ui"), server)
#shiny run --reload webb.py

