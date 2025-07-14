import streamlit as st
import rasterio
import numpy as np
import tempfile
import os

def kompreset_raster(input_ceļš, output_ceļš, kompresijas_metode='jpeg', kvalitāte=50):
    with rasterio.open(input_ceļš) as src:
        dati = src.read()
        meta = src.meta.copy()

    if np.max(dati) <= 255 and np.min(dati) >= 0:
        dati = dati.astype('uint8')
        meta['dtype'] = 'uint8'

    if dati.shape[0] == 4:
        dati = dati[:3]
        meta['count'] = 3

    if kompresijas_metode.lower() == 'jpeg':
        meta.update({
            "compress": "jpeg",
            "photometric": "ycbcr",
            "quality": kvalitāte
        })

    meta.update({
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256
    })

    with rasterio.open(output_ceļš, "w", **meta) as dst:
        dst.write(dati)
    return True

st.set_page_config(page_title="Ortofoto kompresēšanas rīks", layout="centered")

st.title("Ortofoto kompresēšanas rīks")

uploaded_file = st.file_uploader("Izvēlieties ievades TIFF failu:", type=["tif", "tiff"])

kvalitāte = st.slider("Kompresijas kvalitāte (10-100)", min_value=10, max_value=100, value=50)

if uploaded_file is not None:
    base_name = os.path.splitext(uploaded_file.name)[0]
    default_output_name = base_name + "_compressed.tif"
    output_name = st.text_input("Izvades faila nosaukums:", value=default_output_name)
else:
    output_name = st.text_input("Izvades faila nosaukums:", value="ortofoto_compressed.tif", disabled=True)

if st.button("Kompresēt", disabled=(uploaded_file is None)):
    with st.spinner("Kompresē..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as temp_input:
            temp_input.write(uploaded_file.read())
            temp_input.flush()
            temp_input_path = temp_input.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as temp_output:
            temp_output_path = temp_output.name

        try:
            kompreset_raster(temp_input_path, temp_output_path, kvalitāte=kvalitāte)
            with open(temp_output_path, "rb") as f:
                st.success("Fails veiksmīgi kompresēts!")
                st.download_button(
                    label="Lejupielādēt kompresēto TIFF",
                    data=f,
                    file_name=output_name,
                    mime="image/tiff"
                )
        except Exception as e:
            st.error(f"Kļūda kompresējot failu: {e}")
        finally:
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)
