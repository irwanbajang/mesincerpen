from groq import Groq
import streamlit as st

st.set_page_config(
    page_title="Mesin Cerpen Alia Katarina", page_icon="🖋️", layout="centered"
)

st.title("🖋️ Mesin Cerpen Otomatis")
st.write(
    "Aplikasi ringkas pembuat cerpen utuh berbasis Groq (Llama 3.3 70B)."
)

# Menggunakan form agar tidak terjadi eksekusi berulang saat mengetik
with st.form("form_cerpen"):
  api_key = st.text_input(
      "Masukkan Groq API Key:",
      type="password",
      help="Dapatkan gratis di console.groq.com",
  )

  col1, col2 = st.columns(2)
  with col1:
    latar = st.text_input("Latar Tempat & Waktu:", value="Semarang, hujan malam")
  with col2:
    nuansa = st.selectbox(
        "Nuansa / Genre:",
        [
            "Dark Realism",
            "Misteri / Detektif",
            "Drama Psikologis",
            "Melankolis Tajam",
        ],
    )

  gaya_bahasa = st.text_area(
      "Aturan Gaya Bahasa (System Prompt):",
      value=(
          "Bertindaklah sebagai Alia Katarina. Tulis cerpen bahasa Indonesia"
          " yang tajam, dingin, dan tidak bertele-tele. Dilarang menceramahi"
          " pembaca, dilarang menggunakan klise AI, dan dilarang keras"
          " menggunakan tanda baca em-dash (—). Akhiri cerita tanpa penyelesaian"
          " klise."
      ),
      height=110,
  )

  premis = st.text_area(
      "Premis / Ide Cerita (2-4 kalimat):",
      value=(
          "Almira menemukan sebuah lukisan tua di gudang barang antik Semarang"
          " yang memuat wajahnya sendiri dari dua puluh tahun lalu. Banyu,"
          " kurator sinis yang menemaninya, menyadari tanda tangan pelukisnya"
          " milik orang yang sudah lama dinyatakan hilang."
      ),
      height=130,
  )

  submit_btn = st.form_submit_button("✨ Tulis Cerpen Sekarang")

if submit_btn:
  if not api_key:
    st.error("Masukkan Groq API Key terlebih dahulu.")
  elif not premis.strip():
    st.error("Isi premis atau ide ceritanya terlebih dahulu.")
  else:
    with st.spinner("Sedang merangkai cerpen..."):
      try:
        client = Groq(api_key=api_key)

        prompt_user = f"""
Tuliskan sebuah cerpen utuh (sekitar 1.000 - 1.500 kata) berdasarkan detail berikut:
- Latar: {latar}
- Nuansa: {nuansa}
- Premis: {premis}

Instruksi tambahan:
- Buat judul cerpen yang kuat di baris paling atas.
- Langsung masuk ke adegan pembuka yang memikat tanpa kalimat pengantar atau penutup dari AI.
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": gaya_bahasa},
                {"role": "user", "content": prompt_user},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.75,
            max_tokens=4096,
        )

        hasil_cerpen = chat_completion.choices[0].message.content

        st.success("Cerpen selesai ditulis!")
        st.markdown("---")
        st.markdown(hasil_cerpen)
        st.markdown("---")

        st.download_button(
            label="📥 Unduh Cerpen (.txt)",
            data=hasil_cerpen,
            file_name="Cerpen_Alia_Katarina.txt",
            mime="text/plain",
        )

      except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
