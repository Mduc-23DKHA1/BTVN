import sqlite3
import time

DATABASE_NAME = "AirQualityIndex.db"


def show():

    print("=" * 30)

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    sql = """
    SELECT
        date,
        AQI
    FROM AQI
    WHERE AQI IS NOT NULL
    ORDER BY date DESC
    LIMIT 1;
    """

    cursor.execute(sql)

    ket_qua = cursor.fetchone()

    if ket_qua:
        print(f"Ngày gần nhất: {ket_qua[0]}")
        print(f"Chỉ số AQI: {ket_qua[1]}")

    conn.close()

    return ket_qua


def phanloai():
    print("=" * 30)

    year = int(input("Nhập năm: "))

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    sql = """
    WITH categories(id, phan_loai, min_aqi, max_aqi) AS (
        VALUES
            (1, 'Tốt', 0, 50),
            (2, 'Trung bình', 51, 100),
            (3, 'Kém', 101, 150),
            (4, 'Không tốt cho sức khỏe', 151, 200),
            (5, 'Rất không tốt', 201, 300),
            (6, 'Nguy hiểm', 301, NULL)
    )

    SELECT
        c.phan_loai,
        COUNT(a.AQI) AS so_luong

    FROM categories c

    LEFT JOIN AQI a
        ON strftime('%Y', a.date) = ?
        AND (
            (c.max_aqi IS NOT NULL
             AND a.AQI BETWEEN c.min_aqi AND c.max_aqi)

            OR

            (c.max_aqi IS NULL
             AND a.AQI >= c.min_aqi)
        )

    GROUP BY
        c.id,
        c.phan_loai

    ORDER BY c.id;
    """

    cursor.execute(sql, (str(year),))
    ket_qua = cursor.fetchall()

    for row in ket_qua:
        print(row)

    conn.close()
    return ket_qua


def trungbinh():

    print("=" * 30)

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    sql = """
    WITH ngay_cuoi AS (
        SELECT MAX(date) AS ngay_max
        FROM AQI
    ),

    du_lieu AS (
        SELECT
            date,
            AQI
        FROM AQI
        WHERE AQI IS NOT NULL
    )

    SELECT
        'Tuần gần nhất' AS thoi_gian,
        AVG(AQI) AS aqi_trung_binh
    FROM du_lieu, ngay_cuoi
    WHERE date BETWEEN date(ngay_max, '-6 days') AND ngay_max

    UNION ALL

    SELECT
        'Tháng gần nhất' AS thoi_gian,
        AVG(AQI) AS aqi_trung_binh
    FROM du_lieu, ngay_cuoi
    WHERE strftime('%Y-%m', date) = strftime('%Y-%m', ngay_max)

    UNION ALL

    SELECT
        'Năm gần nhất' AS thoi_gian,
        AVG(AQI) AS aqi_trung_binh
    FROM du_lieu, ngay_cuoi
    WHERE strftime('%Y', date) = strftime('%Y', ngay_max);
    """

    cursor.execute(sql)

    ket_qua = cursor.fetchall()

    for row in ket_qua:
        print(row)

    conn.close()

    return ket_qua


def top():

    print("=" * 30)

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    n = int(input("Nhập số ngày muốn lấy Top: "))

    # Top ngày có AQI thấp nhất
    sql_thap = """
    SELECT date, AQI
    FROM AQI
    WHERE AQI IS NOT NULL
    ORDER BY AQI ASC
    LIMIT ?
    """

    cursor.execute(sql_thap, (n,))
    top_thap = cursor.fetchall()

    # Top ngày có AQI cao nhất
    sql_cao = """
    SELECT date, AQI
    FROM AQI
    WHERE AQI IS NOT NULL
    ORDER BY AQI DESC
    LIMIT ?
    """

    cursor.execute(sql_cao, (n,))
    top_cao = cursor.fetchall()

    conn.close()

    return top_thap, top_cao


def trungbinhtruot():
    print("=" * 30)

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    sql = """
    WITH trung_binh_truot AS (
        SELECT
            date,
            AQI,

            AVG(AQI) OVER (
                ORDER BY date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) AS TB_7_NGAY,

            AVG(AQI) OVER (
                ORDER BY date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ) AS TB_30_NGAY,

            AVG(AQI) OVER (
                ORDER BY date
                ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
            ) AS TB_90_NGAY,

            AVG(AQI) OVER (
                ORDER BY date
                ROWS BETWEEN 179 PRECEDING AND CURRENT ROW
            ) AS TB_180_NGAY

        FROM AQI
        WHERE AQI IS NOT NULL
    )

    SELECT
        date,
        TB_7_NGAY,
        TB_30_NGAY,
        TB_90_NGAY,
        TB_180_NGAY
    FROM trung_binh_truot
    ORDER BY date DESC
    LIMIT 1;
    """

    cursor.execute(sql)

    ket_qua = cursor.fetchone()

    if ket_qua:
        print(f"Ngày: {ket_qua[0]}")
        print(f"Trung bình trượt 7 ngày : {ket_qua[1]:.2f}")
        print(f"Trung bình trượt 30 ngày : {ket_qua[2]:.2f}")
        print(f"Trung bình trượt 90 ngày: {ket_qua[3]:.2f}")
        print(f"Trung bình trượt 180 ngày: {ket_qua[4]:.2f}")

    conn.close()

    return ket_qua


def thongke():

    print("=" * 30)

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # =========================
    # THỐNG KÊ THEO THÁNG
    # =========================

    sql_thang = """
    SELECT
        strftime('%Y-%m', date) AS thang,
        AVG(AQI) AS aqi_trung_binh,
        MIN(AQI) AS aqi_thap_nhat,
        MAX(AQI) AS aqi_cao_nhat,
        COUNT(AQI) AS so_ngay
    FROM AQI
    WHERE AQI IS NOT NULL
    GROUP BY thang
    ORDER BY thang;
    """

    cursor.execute(sql_thang)
    ket_qua_thang = cursor.fetchall()

    # =========================
    # THỐNG KÊ THEO QUÝ
    # =========================

    sql_quy = """
    SELECT
        strftime('%Y', date) AS nam,

        CASE
            WHEN CAST(strftime('%m', date) AS INTEGER) BETWEEN 1 AND 3
                THEN 'Q1'

            WHEN CAST(strftime('%m', date) AS INTEGER) BETWEEN 4 AND 6
                THEN 'Q2'

            WHEN CAST(strftime('%m', date) AS INTEGER) BETWEEN 7 AND 9
                THEN 'Q3'

            ELSE 'Q4'
        END AS quy,

        AVG(AQI) AS aqi_trung_binh,
        MIN(AQI) AS aqi_thap_nhat,
        MAX(AQI) AS aqi_cao_nhat,
        COUNT(AQI) AS so_ngay

    FROM AQI

    WHERE AQI IS NOT NULL

    GROUP BY nam, quy
    ORDER BY nam, quy;
    """

    cursor.execute(sql_quy)
    ket_qua_quy = cursor.fetchall()

    # =========================
    # THỐNG KÊ THEO NĂM
    # =========================

    sql_nam = """
    SELECT
        strftime('%Y', date) AS nam,
        AVG(AQI) AS aqi_trung_binh,
        MIN(AQI) AS aqi_thap_nhat,
        MAX(AQI) AS aqi_cao_nhat,
        COUNT(AQI) AS so_ngay
    FROM AQI
    WHERE AQI IS NOT NULL
    GROUP BY nam
    ORDER BY nam;
    """

    cursor.execute(sql_nam)
    ket_qua_nam = cursor.fetchall()

    conn.close()

    return ket_qua_thang, ket_qua_quy, ket_qua_nam


def ngay():
    print("=" * 30)

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    sql = """
    WITH xep_hang AS (

        SELECT
            date,
            AQI,

            strftime('%Y-%m', date) AS thang,

            ROW_NUMBER() OVER (
                PARTITION BY strftime('%Y-%m', date)
                ORDER BY AQI DESC
            ) AS thu_hang

        FROM AQI

        WHERE AQI IS NOT NULL
    )

    SELECT
        thang,
        date,
        AQI

    FROM xep_hang

    WHERE thu_hang = 1

    ORDER BY thang DESC;
    """

    cursor.execute(sql)

    ket_qua = cursor.fetchall()

    print("\n--- NGÀY Ô NHIỄM NHẤT MỖI THÁNG ---")

    for row in ket_qua:
        print(f"Tháng: {row[0]} | " f"Ngày: {row[1]} | " f"AQI: {row[2]}")

    conn.close()

    return ket_qua


def main():
    while True:
        print(
            """
=============================================================================
CHƯƠNG TRÌNH QUẢN LÝ CHẤT LƯỢNG KHÔNG KHÍ TẠI TP.HCM
1. Xem ngày gần nhất
2. Phân loại chất lượng không khí (theo tháng, theo năm, tất cả các năm)   
3. Chỉ số chất lượng không khí trung bình theo (tuần / tháng / quý) gần nhất
4. Top ngày có chỉ số không khí cao nhất / thấp nhất
5. Chỉ số chất lượng không khí trung bình trượt (7/30/90/180 ngày)
6. Thống kê chất lượng không khí theo (tháng / quý / năm)
7. Ngày ô nhiễm nhất mỗi tháng
=============================================================================
Nhập lựa chọn: """,
            end=" ",
        )
        try:
            choice = int(input())
        except:
            print("Chương trình dừng!")
            break

        if choice == 1:
            show()
        elif choice == 2:
            phanloai()
        elif choice == 3:
            trungbinh()
        elif choice == 4:
            t = top()
            if input("Bạn có muốn xem Top ngày ô nhiễm nhất không?(c/k)") == "c":
                print("\n--- Top ngày có chỉ số AQI cao nhất ---")
                for i in t[1]:
                    print(i)
            if input("Bạn có muốn xem Top ngày ít ô nhiễm nhất không?(c/k)") == "c":
                print("\n--- Top ngày có chỉ số AQI thấp nhất ---")
                for i in t[0]:
                    print(i)
        elif choice == 5:
            trungbinhtruot()
        elif choice == 6:
            thang, quy, nam = thongke()

            if input("Bạn có muốn xem thống kê theo tháng không?(c/k)") == "c":
                print("\n--- THỐNG KÊ THEO THÁNG ---")
                for row in thang:
                    print(
                        f"Tháng: {row[0]} | "
                        f"TB: {row[1]:.2f} | "
                        f"Thấp nhất: {row[2]} | "
                        f"Cao nhất: {row[3]} | "
                        f"Số ngày: {row[4]}"
                    )

            if input("Bạn có muốn xem thống kê theo quý không?(c/k)") == "c":
                print("\n--- THỐNG KÊ THEO QUÝ ---")
                for row in quy:
                    print(
                        f"Năm: {row[0]} | "
                        f"Quý: {row[1]} | "
                        f"TB: {row[2]:.2f} | "
                        f"Thấp nhất: {row[3]} | "
                        f"Cao nhất: {row[4]} | "
                        f"Số ngày: {row[5]}"
                    )

            if input("Bạn có muốn xem thống kê theo năm không?(c/k)") == "c":
                print("\n--- THỐNG KÊ THEO NĂM ---")
                for row in nam:
                    print(
                        f"Năm: {row[0]} | "
                        f"TB: {row[1]:.2f} | "
                        f"Thấp nhất: {row[2]} | "
                        f"Cao nhất: {row[3]} | "
                        f"Số ngày: {row[4]}"
                    )
        elif choice == 7:
            ngay()
        time.sleep(2)


if __name__ == "__main__":
    main()
