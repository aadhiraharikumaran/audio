if selected_voice:
    text_input = st.text_area("Enter text to convert to speech (max 2000 characters)")

    if st.button("Generate Speech"):
        if len(text_input) > 2000:
            st.error("Text exceeds 2000 character limit. Please shorten your input.")
        else:
            payload = {
                "text": text_input,
                "voice": selected_voice,
                "output_format": "mp3",
                "voice_engine": "PlayHT2.0"
            }
            headers = {
                "accept": "audio/mpeg",
                "content-type": "application/json",
                "X-User-ID": USER_ID,
                "Authorization": f"Bearer {API_KEY}"
            }

            try:
                with st.spinner("Generating audio..."):
                    response = requests.post(GENERATE_AUDIO_URL, json=payload, headers=headers, stream=True)
                    
                    # Log full response details
                    logger.info(f"TTS API Response Status: {response.status_code}")
                    logger.info(f"TTS API Response Headers: {response.headers}")

                    if response.status_code == 403:
                        st.error("❌ Access Denied: Your API key may not have permission for text-to-speech. Check Play.ht API settings.")
                        logger.error(f"403 Forbidden Error: {response.text}")

                    elif response.status_code == 401:
                        st.error("❌ Unauthorized: Your API key might be incorrect or expired.")
                        logger.error(f"401 Unauthorized Error: {response.text}")

                    elif response.status_code == 200:
                        # Save and play the audio
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        mp3_filename = f"audio_{timestamp}.mp3"
                        mp3_filepath = os.path.join(AUDIO_FOLDER, mp3_filename)

                        with open(mp3_filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        st.success(f"✅ Audio generated successfully: {mp3_filename}")
                        st.audio(mp3_filepath, format="audio/mp3")

                    else:
                        st.error(f"⚠️ Unexpected Error: {response.status_code}")
                        logger.error(f"Unexpected Error {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ API Request Failed: {str(e)}")
                logger.error(f"API Request Exception: {str(e)}")
