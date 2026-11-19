from groq import Groq
import streamlit as st

st.set_page_config(
    page_title="Mesin Cerpen Alia Katarina", page_icon="🖋️", layout="centered"
)

st.title("🖋️ Mesin Cerpen Otomatis")
st.write("Aplikasi ringkas pembuat cerpen utuh berbasis Groq.")

default_api_key = ""
try:
  if "GROQ_API_KEY" in st.secrets:
    default_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
  pass

api_key = st.text_input(
    "Groq API Key (otomatis terisi jika sudah diset di Secrets):",
    value=default_api_key,
    type="password",
)

available_models = []
if api_key:
  try:
    temp_client = Groq(api_key=api_key)
    models_response = temp_client.models.list()
    raw_ids = sorted([m.id for m in models_response.data])
    filtered_ids = [
        mid
        for mid in raw_ids
        if not any(
            bad in mid.lower()
            for bad in [
                "guard",
                "whisper",
                "safeguard",
                "moderation",
                "orpheus",
                "distil",
            ]
        )
    ]
    available_models = filtered_ids if filtered_ids else raw_ids
  except Exception as e:
    st.warning(f"Belum bisa memuat daftar model otomatis: {e}")

with st.form("form_cerpen"):
  if available_models:
    default_idx = 0
    for keyword in ["120b", "qwen", "20b", "gpt-oss"]:
      matched = next(
          (i for i, m_id in enumerate(available_models) if keyword in m_id.lower()),
          None,
      )
      if matched is not None:
        default_idx = matched
        break

    selected_model = st.selectbox(
        "Pilih Model Groq Aktif:",
        options=available_models,
        index=default_idx,
    )
  else:
    selected_model = st.text_input(
        "ID Model Groq:",
        value="",
        help="Masukkan API Key di atas agar daftar model aktif muncul otomatis.",
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
          " yang baku, tajam, dingin, dan tidak bertele-tele. Gunakan nama"
          " tokoh sesuai premis secara konsisten dan jangan mengarang nama"
          " baru yang tidak diminta. Dilarang menceramahi pembaca, dilarang"
          " menggunakan klise AI, dan dilarang keras menggunakan tanda baca"
          " em-dash (—). Akhiri cerita tanpa penyelesaian klise dan jangan"
          " mengulang kalimat yang sama."
      ),
      height=130,
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
  elif not selected_model.strip():
    st.error("Pilih atau masukkan ID model Groq terlebih dahulu.")
  elif not premis.strip():
    st.error("Isi premis atau ide ceritanya terlebih dahulu.")
  else:
    with st.spinner("Sedang merangkai cerpen..."):
      try:
        client = Groq(api_key=api_key)

        prompt_user = f"""
Tuliskan sebuah cerpen bahasa Indonesia yang rapi, wajar, dan utuh (sekitar 700 - 1.100 kata) berdasarkan detail berikut:
- Latar: {latar}
- Nuansa: {nuansa}
- Premis: {premis}

Instruksi tambahan:
- Buat judul cerpen yang tajam di baris paling atas.
- Gunakan nama tokoh yang konsisten sesuai premis (Almira dan Banyu).
- Langsung masuk ke adegan pembuka tanpa kalimat pengantar atau penutup dari AI, dan pastikan setiap kalimat memiliki struktur bahasa Indonesia yang jelas.
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": gaya_bahasa},
                {"role": "user", "content": prompt_user},
            ],
            model=selected_model.strip(),
            temperature=0.55,
            max_tokens=2048,
            frequency_penalty=0.5,
        )

        hasil_cerpen = chat_completion.choices[0].message.content

        st.success(
            f"Cerpen selesai ditulis menggunakan model `{selected_model}`!"
        )
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
