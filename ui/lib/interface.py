"""Gradio interface for Phonikud TTS."""

import os
import gradio as gr
from . import api
from .aac_keyboard import create_aac_interface, get_predictions


def create_interface():
    """Create the main Gradio interface."""
    # Initial state
    is_available, available_voices = False, []

    # Check if local saving is disabled
    disable_local_saving = os.getenv("DISABLE_LOCAL_SAVING", "false").lower() == "true"

    # Create theme for Gradio 6.x
    theme = gr.themes.Base(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    )

    css = """
        /* Force dark background */
        html, body, .gradio-container {
            background: #171717 !important;
            min-height: 100vh !important;
        }

        /* Global styles */
        * { box-sizing: border-box; }

        body {
            background: #171717;
            min-height: 100vh;
        }

        /* Main container */
        .container {
            max-width: 97%;
            width: 1800px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }

        /* Card styles - monochrome with hover effect */
        .card {
            background: rgba(40, 40, 40, 0.9);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 20px;
            overflow: visible !important;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            border-color: #F97317;
            box-shadow: 0 0 20px rgba(249, 115, 23, 0.15);
        }

        /* Floating Navbar */
        .navbar {
            position: fixed;
            top: 16px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 1200px;
            background: rgba(40, 40, 40, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 0 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            height: 48px;
            line-height: 48px;
        }
        
        .navbar.scrolled {
            top: 12px;
            width: 60%;
            max-width: 600px;
            padding: 0 20px;
            border-radius: 50px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            height: 40px;
            line-height: 40px;
        }
        
        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            height: 100%;
        }
        
        .navbar-brand h1 {
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            margin: 0 !important;
            padding: 0 !important;
            letter-spacing: -0.5px;
            transition: font-size 0.3s ease;
            line-height: inherit !important;
            height: 100%;
            display: flex;
            align-items: center;
        }
        
        .navbar.scrolled .navbar-brand h1 {
            font-size: 15px;
        }
        
        .navbar-links {
            display: flex;
            gap: 4px;
            align-items: center;
            height: 100%;
        }
        
        .navbar-links a {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.7) !important;
            text-decoration: none !important;
            padding: 6px 12px;
            border-radius: 6px;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            height: auto;
        }
        
        .navbar-links a:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #fff !important;
        }
        
        .navbar-links a svg {
            flex-shrink: 0;
        }
        
        /* Mobile Responsive Styles */
        @media (max-width: 768px) {
            .navbar {
                width: 95%;
                padding: 0 12px;
                height: 44px;
                line-height: 44px;
                top: 8px;
            }
            
            .navbar.scrolled {
                width: 95%;
                padding: 0 12px;
                height: 44px;
                line-height: 44px;
                top: 8px;
                border-radius: 12px;
            }
            
            .navbar-brand h1 {
                font-size: 14px !important;
            }
            
            .navbar-links a {
                padding: 4px 8px;
                font-size: 11px;
                gap: 4px;
            }
            
            .navbar-links a svg {
                width: 14px;
                height: 14px;
            }
            
            .header {
                padding: 70px 0 20px;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .header p {
                font-size: 14px;
            }
            
            .card {
                padding: 20px;
                border-radius: 12px;
            }
            
            .container {
                padding: 0 8px;
            }
            
            .btn-row {
                flex-direction: column;
                gap: 8px;
            }
        }

        /* Header */
        .header {
            text-align: center;
            padding: 100px 0 30px;
        }
        .header h1 {
            font-size: 36px;
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 8px 0;
            letter-spacing: -1px;
            text-shadow: 0 0 40px rgba(120, 120, 255, 0.3);
        }
        .header p {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.5);
            margin: 0;
            font-weight: 400;
        }

        /* Section titles */
        .section-title {
            font-size: 11px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.4);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .section-title::after {
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, rgba(255,255,255,0.1), transparent);
        }

        /* Phoneme box */
        .phoneme-box {
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
            direction: ltr;
            background: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 30px 0;
            color: rgba(255, 255, 255, 0.3);
            font-size: 12px;
        }
        .footer a {
            color: rgba(255, 255, 255, 0.5);
            text-decoration: none;
            transition: color 0.2s;
        }
        .footer a:hover {
            color: rgba(255, 255, 255, 0.8);
        }

        /* Override Gradio dark theme */
        .gradio-container {
            background: transparent !important;
        }

        /* Input/Output boxes styling */
        .input-box textarea,
        .output-box textarea {
            background: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            color: #fff !important;
            font-size: 15px !important;
        }
        .input-box textarea::placeholder {
            color: rgba(255, 255, 255, 0.3) !important;
        }
        .input-box textarea:focus {
            border-color: rgba(100, 100, 255, 0.4) !important;
            box-shadow: 0 0 0 3px rgba(100, 100, 255, 0.1) !important;
        }

        /* Labels */
        label {
            color: rgba(255, 255, 255, 0.7) !important;
            font-weight: 500 !important;
            font-size: 13px !important;
        }

        /* Dropdown styling */
        .gr-dropdown {
            background: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
        }

        /* Fix dropdown popup positioning */
        .gr-dropdown-container {
            position: relative !important;
        }

        /* Style the dropdown options list */
        .dropdown-options,
        .gradio-container .dropdown ul,
        ul[class*="options"] {
            background: rgba(30, 30, 40, 0.98) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 8px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
            z-index: 9999 !important;
            position: absolute !important;
        }

        .dropdown-options li,
        .gradio-container .dropdown ul li,
        ul[class*="options"] li {
            color: #fff !important;
            padding: 10px 16px !important;
        }

        .dropdown-options li:hover,
        .gradio-container .dropdown ul li:hover,
        ul[class*="options"] li:hover {
            background: rgba(100, 100, 255, 0.2) !important;
        }

        /* Slider styling */
        input[type="range"] {
            background: rgba(255, 255, 255, 0.1) !important;
        }

        /* Audio player */
        .audio-container {
            background: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            padding: 16px !important;
        }

        /* Button row spacing */
        .btn-row {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }
        
        /* Primary button glow and animation */
        .primary-btn,
        button.primary,
        button[class*="primary"],
        .gr-button-primary,
        .btn-primary {
            background: linear-gradient(135deg, #F97317, #ea580c) !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(249, 115, 23, 0.4) !important;
            transition: all 0.3s ease !important;
            position: relative;
            overflow: hidden;
        }
        
        .primary-btn:hover,
        button.primary:hover,
        button[class*="primary"]:hover,
        .gr-button-primary:hover,
        .btn-primary:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(249, 115, 23, 0.6) !important;
        }
        
        .primary-btn:active,
        button.primary:active,
        button[class*="primary"]:active {
            transform: translateY(0) !important;
        }
        
        /* Tabs styling */
        .tabs {
            margin-top: 10px;
        }
        
        button.svelte-1b6l99q.selected {
            background: rgba(249, 115, 23, 0.2) !important;
            border-color: #F97317 !important;
        }

        /* AAC specific styles */
        .aac-container {
            padding: 10px;
        }
        
        .sentence-display {
            background: rgba(0, 0, 0, 0.4);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            min-height: 80px;
            margin-bottom: 15px;
            font-size: 28px;
            color: #fff;
            text-align: right;
            direction: rtl;
        }
        
        .word-btn {
            min-height: 60px !important;
            font-size: 20px !important;
        }
        
        .word-btn-small {
            min-height: 40px !important;
            font-size: 16px !important;
            padding: 4px 8px !important;
        }
        
        .word-btn-tiny {
            min-height: 44px !important;
            font-size: 16px !important;
            padding: 4px 10px !important;
        }
        
        /* Mobile and tablet optimization */
        @media (max-width: 1024px) {
            .word-btn-tiny {
                min-height: 52px !important;
                font-size: 18px !important;
                padding: 8px 12px !important;
            }
            
            .word-btn-small {
                min-height: 50px !important;
                font-size: 18px !important;
            }
            
            .aac-section-label {
                font-size: 16px !important;
            }
            
            .sentence-display {
                font-size: 24px !important;
                min-height: 100px !important;
            }
        }
        
        /* Custom text input styling */
        .custom-text-input {
            background: rgba(0, 0, 0, 0.4) !important;
            border: 2px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            font-size: 18px !important;
            direction: rtl !important;
        }
        
        /* Punctuation buttons */
        .punctuation-btn {
            min-width: 44px !important;
            font-size: 20px !important;
            font-weight: bold !important;
        }
        
        /* Copy notification */
        .copy-notification {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(249, 115, 23, 0.95);
            color: white;
            padding: 16px 32px;
            border-radius: 12px;
            font-size: 18px;
            z-index: 9999;
            animation: fadeInOut 2s ease-in-out;
        }
        
        @keyframes fadeInOut {
            0% { opacity: 0; }
            20% { opacity: 1; }
            80% { opacity: 1; }
            100% { opacity: 0; }
        }
        
        .speak-btn {
            background: linear-gradient(135deg, #F97317, #ea580c) !important;
            font-size: 24px !important;
            min-height: 70px !important;
        }
        
        /* RTL Support for Hebrew - reverse button rows */
        .aac-container {
            direction: rtl !important;
        }
        
        .aac-container > .gradio-row {
            flex-direction: row-reverse !important;
        }
        
        .aac-container button {
            direction: rtl !important;
        }
        
        /* AAC Section labels with RTL */
        .aac-section-label {
            font-size: 14px;
            color: rgba(255,255,255,0.5);
            margin: 15px 0 10px;
            direction: rtl;
            text-align: right;
        }
        """

    with gr.Blocks(title="Phonikud TTS WebUI") as demo:
        # Inject CSS via HTML component (works in all Gradio versions)
        gr.HTML(f"<style>{css}</style>")

        # Floating Navbar
        gr.HTML(
            value="""
            <nav class="navbar" id="navbar">
                <div class="navbar-brand">
                    <h1>Phonikud TTS WebUI</h1>
                </div>
                <div class="navbar-links">
                    <a href="https://github.com/thewh1teagle/phonikud" target="_blank">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                        </svg>
                        GitHub
                    </a>
                    <a href="/docs" target="_blank">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                        </svg>
                        API
                    </a>
                </div>
            </nav>
            <script>
            (function() {
                window.addEventListener('scroll', function() {
                    const navbar = document.getElementById('navbar');
                    if (navbar) {
                        if (window.scrollY > 50) {
                            navbar.classList.add('scrolled');
                        } else {
                            navbar.classList.remove('scrolled');
                        }
                    }
                });
            })();
            </script>
            """,
        )

        with gr.Column(elem_classes=["container"]):
            # Header
            gr.HTML(
                value="""
                <div class="header">
                    <h1>Phonikud TTS WebUI</h1>
                    <p>Hebrew Text-to-Speech</p>
                </div>
                """,
            )

            # Tabs for TTS and AAC modes
            with gr.Tabs() as tabs:
                # TTS Tab
                with gr.TabItem("Text to Speech"):
                    # Main content card
                    with gr.Column(elem_classes=["card"]):
                        with gr.Row():
                            # Left column - Input
                            with gr.Column(scale=3):
                                gr.HTML('<div class="section-title">Input</div>')
                                text_input = gr.Textbox(
                                    label="Hebrew Text",
                                    placeholder="Enter Hebrew text here...",
                                    value="שרה שרה שיר",
                                    lines=5,
                                    rtl=True,
                                    show_label=False,
                                    elem_classes=["input-box"],
                                )

                                with gr.Row():
                                    phonemize_btn = gr.Button("Show Phonemes", variant="secondary", size="sm")

                                phoneme_output = gr.Textbox(
                                    label="Phonemes",
                                    visible=True,
                                    lines=2,
                                    interactive=False,
                                    elem_classes=["phoneme-box"],
                                    show_label=True,
                                )

                            # Right column - Settings
                            with gr.Column(scale=2):
                                gr.HTML('<div class="section-title">Settings</div>')

                                # Status button
                                status_btn = gr.Button(
                                    value="Checking service...",
                                    interactive=False,
                                    variant="secondary",
                                    size="sm",
                                )

                                # Engine selection
                                engine_dropdown = gr.Dropdown(
                                    label="Engine",
                                    choices=["piper"],
                                    value="piper",
                                    show_label=True,
                                    interactive=False,
                                )

                                # Voice selection
                                voice_dropdown = gr.Dropdown(
                                    label="Voice",
                                    choices=[],
                                    value=None,
                                    show_label=True,
                                )

                                # Speed control
                                speed_slider = gr.Slider(
                                    label="Speed",
                                    minimum=0.5,
                                    maximum=2.0,
                                    value=1.0,
                                    step=0.1,
                                )

                                # Volume control
                                volume_slider = gr.Slider(
                                    label="Volume",
                                    minimum=0.5,
                                    maximum=5.0,
                                    value=2.0,
                                    step=0.5,
                                )

                        # Generate buttons
                        with gr.Row(elem_classes=["btn-row"]):
                            generate_btn = gr.Button("Generate Speech", variant="primary", size="lg", scale=2)
                            generate_with_phonemes_btn = gr.Button("Generate with Phonemes", variant="secondary", size="lg", scale=2)

                    # Output card
                    with gr.Column(elem_classes=["card"]):
                        gr.HTML('<div class="section-title">Output</div>')

                        audio_output = gr.Audio(
                            label="Audio",
                            visible=True,
                            interactive=False,
                            type="filepath",
                            show_label=False,
                            elem_classes=["audio-container"],
                        )

                        with gr.Row():
                            with gr.Column(scale=2):
                                vocalized_output = gr.Textbox(
                                    label="Vocalized Text",
                                    interactive=False,
                                    lines=2,
                                    rtl=True,
                                    elem_classes=["output-box"],
                                )

                            with gr.Column(scale=1):
                                info_output = gr.Textbox(
                                    label="Info",
                                    interactive=False,
                                    lines=2,
                                    elem_classes=["output-box"],
                                )

                # AAC Tab
                with gr.TabItem("AAC Keyboard"):
                    with gr.Column(elem_classes=["card", "aac-container"]):
                        # Audio output at top with autoplay
                        aac_audio_output = gr.Audio(
                            label="Audio Output",
                            visible=True,
                            interactive=False,
                            type="filepath",
                            show_label=False,
                            elem_classes=["audio-container"],
                            autoplay=True,
                        )
                        
                        # Sentence display
                        sentence_display = gr.HTML(
                            value='<div class="sentence-display">הטקסט יופיע כאן...</div>',
                        )
                        
                        # Hidden state for sentence
                        sentence_state = gr.State(value="")
                        
                        # Action buttons
                        with gr.Row():
                            clear_btn = gr.Button("ניקוי טקסט", size="lg", scale=1)
                            backspace_btn = gr.Button("מחיקת מילה אחרונה", size="lg", scale=1)
                            copy_btn = gr.Button("העתק", size="lg", scale=1, variant="secondary")
                            speak_btn = gr.Button("המרה לשמע", size="lg", scale=2, variant="primary", elem_classes=["speak-btn"])
                        
                        # AAC Speed control
                        aac_speed_state = gr.State(value=0.75)
                        with gr.Row():
                            aac_speed_slider = gr.Slider(
                                label="מהירות דיבור",
                                minimum=0.5,
                                maximum=1.5,
                                value=0.75,
                                step=0.1,
                                scale=3,
                            )
                        
                        # Speak mode toggle
                        speak_mode_state = gr.State(value=False)
                        gender_state = gr.State(value="male")  # male or female voice
                        with gr.Row():
                            speak_mode_btn = gr.Button("כפתורי שמע: כבוי", size="lg", variant="secondary")
                            gender_btn = gr.Button("זכר", size="lg", variant="secondary")
                        
                        # Custom Text Input section
                        gr.HTML('<div class="aac-section-label">הקלד טקסט חופשי:</div>')
                        with gr.Row():
                            custom_text_input = gr.Textbox(
                                placeholder="הקלד כאן...",
                                rtl=True,
                                show_label=False,
                                scale=4,
                                elem_classes=["custom-text-input"],
                            )
                            add_custom_text_btn = gr.Button("הוסף", size="lg", variant="primary", scale=1)
                        
                        # Punctuation section
                        gr.HTML('<div class="aac-section-label">פיסוק:</div>')
                        punctuation_btns = []
                        punctuation_marks = ["!", "?", ".", ",", ":", ";", "\"", "'", "..."]
                        with gr.Row():
                            for punct in punctuation_marks:
                                btn = gr.Button(punct, size="sm", elem_classes=["punctuation-btn"], variant="secondary")
                                punctuation_btns.append(btn)
                        
                        # Favorites section
                        gr.HTML('<div class="aac-section-label">משפטים שמורים:</div>')
                        with gr.Row():
                            save_favorite_btn = gr.Button("שמור משפט", size="lg", variant="secondary", scale=1)
                            clear_favorites_btn = gr.Button("נקה שמורים", size="lg", variant="secondary", scale=1)
                        
                        favorites_btns = []
                        default_favorites = ["—", "—", "—", "—", "—", "—", "—", "—"]
                        with gr.Row():
                            for i in range(4):
                                btn = gr.Button(default_favorites[i], size="sm", elem_classes=["word-btn-tiny"])
                                favorites_btns.append(btn)
                        with gr.Row():
                            for i in range(4):
                                btn = gr.Button(default_favorites[i+4], size="sm", elem_classes=["word-btn-tiny"])
                                favorites_btns.append(btn)
                        favorites_state = gr.State(value=[])
                        
                        # Most Used / Favorites section (dynamically updated based on gender)
                        gr.HTML('<div class="aac-section-label">הכי בשימוש:</div>')
                        
                        most_used_state = gr.State(value=[])
                        most_used_btns = []
                        # Male default - will be updated when gender changes
                        default_most_used_male = ["אני", "רוצה", "כן", "לא", "תודה", "בבקשה", "עזרה", "מים"]
                        with gr.Row():
                            for phrase in default_most_used_male[:8]:
                                btn = gr.Button(phrase, size="sm", elem_classes=["word-btn-tiny"], variant="primary")
                                most_used_btns.append(btn)
                        
                        # Question words and common connectors section
                        gr.HTML('<div class="aac-section-label">מילות שאלה וחיבור:</div>')
                        
                        question_connector_btns = []
                        question_words = ["מי?", "מה?", "מתי?", "איפה?", "למה?", "איך?", "כמה?", "איזה?"]
                        with gr.Row():
                            for word in question_words:
                                btn = gr.Button(word, size="sm", elem_classes=["word-btn-tiny"], variant="primary")
                                question_connector_btns.append(btn)
                        
                        connector_words = ["או", "וגם", "אבל", "כי", "אז", "אם", "עם", "בלי"]
                        with gr.Row():
                            for word in connector_words:
                                btn = gr.Button(word, size="sm", elem_classes=["word-btn-tiny"])
                                question_connector_btns.append(btn)
                        
                        # Basic Hebrew grammar words section
                        gr.HTML('<div class="aac-section-label">מילים בסיסיות:</div>')
                        
                        basic_words_btns = []
                        basic_row1 = ["ה", "את", "של", "ל", "מ", "ב", "ו", "זה"]
                        basic_row2 = ["זאת", "אלה", "הזה", "הזאת", "שלי", "שלך", "שלו", "שלה"]
                        with gr.Row():
                            for word in basic_row1:
                                btn = gr.Button(word, size="sm", elem_classes=["word-btn-tiny"], variant="primary")
                                basic_words_btns.append(btn)
                        with gr.Row():
                            for word in basic_row2:
                                btn = gr.Button(word, size="sm", elem_classes=["word-btn-tiny"])
                                basic_words_btns.append(btn)
                        
                        # Functionality/Status words section
                        gr.HTML('<div class="aac-section-label">מצב ותפקוד:</div>')
                        
                        function_words_btns = []
                        function_row1 = ["עובד", "לא עובד", "תקין", "לא תקין", "פתוח", "סגור"]
                        function_row2 = ["יש", "אין", "מלא", "ריק", "חדש", "ישן"]
                        function_row3 = ["מוכן", "לא מוכן", "זמין", "לא זמין", "פעיל", "מכובה"]
                        with gr.Row():
                            for word in function_row1:
                                btn = gr.Button(word, size="sm", elem_classes=["word-btn-tiny"], variant="primary")
                                function_words_btns.append(btn)
                        with gr.Row():
                            for word in function_row2:
                                btn = gr.Button(word, size="sm", elem_classes=["word-btn-tiny"])
                                function_words_btns.append(btn)
                        with gr.Row():
                            for word in function_row3:
                                btn = gr.Button(word, size="sm", elem_classes=["word-btn-tiny"])
                                function_words_btns.append(btn)
                        
                        # Category buttons
                        gr.HTML('<div class="aac-section-label">קטגוריות:</div>')
                        
                        category_btns = []
                        category_row1 = ["הכל", "כינויים", "פעלים", "שאלות", "בסיסי", "אוכל"]
                        category_row2 = ["רגשות", "פעולות", "מקומות", "זמן", "אנשים", "תארים"]
                        category_row3 = ["גוף", "מזג אוויר", "מספרים", "צבעים", "יומיום", "משפחה"]
                        category_row4 = ["פיננסים", "קניות", "רפואה", "תחבורה", "בית", "תקשורת"]
                        category_row5 = ["בגדים", "עבודה", "טכנולוגיה", "בילוי", "חירום", "שאלות מוכנות"]
                        
                        with gr.Row():
                            for cat in category_row1:
                                btn = gr.Button(cat, size="sm", variant="secondary")
                                category_btns.append(btn)
                        
                        with gr.Row():
                            for cat in category_row2:
                                btn = gr.Button(cat, size="sm", variant="secondary")
                                category_btns.append(btn)
                        
                        with gr.Row():
                            for cat in category_row3:
                                btn = gr.Button(cat, size="sm", variant="secondary")
                                category_btns.append(btn)
                        
                        with gr.Row():
                            for cat in category_row4:
                                btn = gr.Button(cat, size="sm", variant="secondary")
                                category_btns.append(btn)
                        
                        with gr.Row():
                            for cat in category_row5:
                                btn = gr.Button(cat, size="sm", variant="secondary")
                                category_btns.append(btn)
                        
                        # Ready Answers Section
                        gr.HTML('<div class="aac-section-label">תשובות מוכנות:</div>')
                        
                        # Ready answer category buttons
                        ready_answer_category_btns = []
                        ready_cat_row1 = ["ברכות", "תגובות", "עזרה", "צרכים", "הרגשות", "שאלות"]
                        ready_cat_row2 = ["חברה", "מקומות", "יומיום", "אוכל", "רפואי", "מזג אוויר"]
                        ready_cat_row3 = ["תקשורת", "קניות", "עבודה", "תחביבים"]
                        ready_cat_row4 = ["טבע", "ספורט", "משפחה"]
                        
                        with gr.Row():
                            for cat_label in ready_cat_row1:
                                btn = gr.Button(cat_label, size="sm", elem_classes=["word-btn-tiny"], variant="primary")
                                ready_answer_category_btns.append(btn)
                        
                        with gr.Row():
                            for cat_label in ready_cat_row2:
                                btn = gr.Button(cat_label, size="sm", elem_classes=["word-btn-tiny"], variant="primary")
                                ready_answer_category_btns.append(btn)
                        
                        with gr.Row():
                            for cat_label in ready_cat_row3:
                                btn = gr.Button(cat_label, size="sm", elem_classes=["word-btn-tiny"], variant="primary")
                                ready_answer_category_btns.append(btn)
                        
                        # Ready answers display (12 buttons for phrases)
                        ready_answer_btns = []
                        default_ready_answers = ["שלום!", "בוקר טוב!", "צהריים טובים!", "ערב טוב!", "לילה טוב!", "מה נשמע?", "איך אתה?", "איך את?", "נעים להכיר", "להתראות!", "יום טוב!", "סוף שבוע נעים"]
                        with gr.Row():
                            for i in range(6):
                                btn = gr.Button(default_ready_answers[i] if i < len(default_ready_answers) else "—", size="sm", elem_classes=["word-btn-tiny"])
                                ready_answer_btns.append(btn)
                        with gr.Row():
                            for i in range(6):
                                btn = gr.Button(default_ready_answers[i+6] if i+6 < len(default_ready_answers) else "—", size="sm", elem_classes=["word-btn-tiny"])
                                ready_answer_btns.append(btn)
                        
                        # Word predictions grid
                        gr.HTML('<div class="aac-section-label">הקש על מילה להוספה למשפט:</div>')
                        
                        # Get initial predictions - 16 words
                        initial_preds = get_predictions("")
                        while len(initial_preds) < 16:
                            initial_preds.append("—")
                        
                        prediction_btns = []
                        with gr.Row():
                            for i in range(8):
                                btn = gr.Button(initial_preds[i], size="sm", elem_classes=["word-btn-tiny"])
                                prediction_btns.append(btn)
                        
                        with gr.Row():
                            for i in range(8):
                                btn = gr.Button(initial_preds[i+8], size="sm", elem_classes=["word-btn-tiny"])
                                prediction_btns.append(btn)
                        
                        # Hidden elements for click-to-remove functionality
                        selected_word_index = gr.State(value=-1)
                        remove_word_btn = gr.Button("", elem_id="remove-word-btn", visible=False)
                        
                        
                        
                        # JavaScript to force audio autoplay
                        gr.HTML(value="""
                        <script>
                        (function() {
                            // Force audio autoplay when src changes
                            const observer = new MutationObserver(() => {
                                const audios = document.querySelectorAll('.aac-container audio');
                                audios.forEach(audio => {
                                    if (audio.src && audio.paused) {
                                        audio.play().catch(() => {});
                                    }
                                });
                            });
                            
                            setTimeout(() => {
                                observer.observe(document.body, { childList: true, subtree: true, attributes: true });
                            }, 1000);
                        })();
                        </script>
                        """)

            # Footer
            gr.HTML(
                value="""
                <div class="footer">
                    Powered by <a href="https://github.com/thewh1teagle/phonikud" target="_blank">Phonikud</a>
                </div>
                """,
            )

        # Event handlers for TTS
        def update_status():
            """Update API status and available voices."""
            try:
                import asyncio

                is_available, voices = asyncio.run(api.check_api_status())
                status = "Available" if is_available else "Connecting..."

                if is_available and voices:
                    default_voice = voices[0] if voices else None
                    return [
                        gr.update(
                            value=f"Service: {status}",
                            variant="primary",
                        ),
                        gr.update(choices=voices, value=default_voice),
                        gr.update(active=False),
                    ]

                return [
                    gr.update(
                        value=f"Service: {status}",
                        variant="secondary",
                    ),
                    gr.update(choices=[], value=None),
                    gr.update(active=True),
                ]
            except Exception as e:
                print(f"Error in status update: {e}")
                return [
                    gr.update(value="Service: Error", variant="stop"),
                    gr.update(choices=[], value=None),
                    gr.update(active=True),
                ]

        def phonemize_handler(text):
            """Handle phonemize button click."""
            if not text.strip():
                return gr.update(value="")

            try:
                import asyncio

                vocalized, phonemes = asyncio.run(api.phonemize_text(text))
                return f"{phonemes}\n\n(Nikud: {vocalized})"
            except Exception as e:
                return f"Error: {str(e)}"

        def generate_handler(text, voice, engine, speed, volume):
            """Handle generate button click."""
            if not text.strip():
                return None, "", "Please enter some text"

            if not voice:
                return None, "", "Please select a voice"

            try:
                import asyncio
                import tempfile

                result = asyncio.run(
                    api.generate_speech_base64(
                        text=text,
                        voice=voice,
                        engine=engine,
                        speed=speed,
                        volume_factor=volume,
                    )
                )

                import base64

                audio_data_uri = result["audio"]
                audio_base64 = audio_data_uri.split(",")[1]
                audio_bytes = base64.b64decode(audio_base64)

                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, "phonikud_output.wav")
                with open(temp_path, "wb") as f:
                    f.write(audio_bytes)

                info = f"Duration: {result['duration_seconds']:.2f}s | Sample Rate: {result['sample_rate']}Hz"

                return temp_path, result["vocalized_text"], info

            except Exception as e:
                return None, "", f"Error: {str(e)}"

        def generate_with_phonemes_handler(text, voice, engine, speed, volume):
            """Handle generate with phonemes button."""
            if not text.strip():
                return "", None, "", "Please enter some text"

            if not voice:
                return "", None, "", "Please select a voice"

            try:
                import asyncio
                import tempfile
                import base64

                vocalized, phonemes = asyncio.run(api.phonemize_text(text))
                phoneme_display = f"{phonemes}\n\n(Nikud: {vocalized})"

                result = asyncio.run(
                    api.generate_speech_base64(
                        text=text,
                        voice=voice,
                        engine=engine,
                        speed=speed,
                        volume_factor=volume,
                    )
                )

                audio_data_uri = result["audio"]
                audio_base64 = audio_data_uri.split(",")[1]
                audio_bytes = base64.b64decode(audio_base64)

                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, "phonikud_output.wav")
                with open(temp_path, "wb") as f:
                    f.write(audio_bytes)

                info = f"Duration: {result['duration_seconds']:.2f}s | Sample Rate: {result['sample_rate']}Hz"

                return phoneme_display, temp_path, result["vocalized_text"], info

            except Exception as e:
                return f"Error: {str(e)}", None, "", f"Error: {str(e)}"

        # AAC Event handlers
        def update_sentence_display(sentence: str) -> str:
            """Update the sentence display HTML with clickable words."""
            if not sentence:
                return '<div class="sentence-display">הטקסט יופיע כאן...</div>'
            
            # Split into words and make each clickable
            words = sentence.strip().split()
            clickable_words = []
            for i, word in enumerate(words):
                # Each word is a clickable span that will trigger removal
                clickable_words.append(f'<span class="sentence-word" data-index="{i}" onclick="window.selectedWordIndex = {i}; document.getElementById(\'remove-word-btn\').click();">{word}</span>')
            
            return f'''<div class="sentence-display" id="sentence-display">{' '.join(clickable_words)}</div>
            <script>
            (function() {{
                // Style for clickable words
                const style = document.createElement('style');
                style.textContent = `
                    .sentence-word {{
                        cursor: pointer;
                        padding: 4px 8px;
                        border-radius: 8px;
                        transition: all 0.2s ease;
                        display: inline-block;
                        margin: 2px;
                    }}
                    .sentence-word:hover {{
                        background: rgba(249, 115, 23, 0.3);
                        color: #F97317;
                    }}
                `;
                document.head.appendChild(style);
            }})();
            </script>'''
        
        def remove_word_at_index(current_sentence: str, index: int):
            """Remove a word at a specific index from the sentence."""
            try:
                words = current_sentence.strip().split()
                
                # Remove word at index if valid, otherwise remove last word
                if index >= 0 and index < len(words):
                    words.pop(index)
                elif words:
                    words.pop()
                
                new_sentence = " ".join(words)
                display = update_sentence_display(new_sentence)
                predictions = get_predictions(new_sentence)
                while len(predictions) < 16:
                    predictions.append("—")
                
                return new_sentence, display, -1, *[gr.update(value=p) for p in predictions]
            except Exception as e:
                print(f"Error removing word: {e}")
                return current_sentence, update_sentence_display(current_sentence), -1, *[gr.update() for _ in range(16)]

        def add_word_to_sentence(word: str, current_sentence: str):
            """Add a word to the sentence and get new predictions."""
            if word == "—":
                return current_sentence, update_sentence_display(current_sentence), *[gr.update() for _ in range(16)]
            
            if current_sentence:
                new_sentence = current_sentence + " " + word
            else:
                new_sentence = word
            
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            while len(predictions) < 16:
                predictions.append("—")
            
            return new_sentence, display, *[gr.update(value=p) for p in predictions]
        
        def delete_specific_word(word_to_delete: str, current_sentence: str):
            """Delete a specific word from the sentence."""
            if not word_to_delete or not current_sentence:
                # Return correct number of outputs even when nothing to delete
                predictions = get_predictions(current_sentence)
                while len(predictions) < 16:
                    predictions.append("—")
                return current_sentence, update_sentence_display(current_sentence), gr.update(), *[gr.update(value=p) for p in predictions]
            
            words = current_sentence.strip().split()
            # Remove the first occurrence of the word
            if word_to_delete in words:
                words.remove(word_to_delete)
            
            new_sentence = " ".join(words)
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            while len(predictions) < 16:
                predictions.append("—")
            
            # Update the word deletion dropdown with remaining words
            word_choices = new_sentence.split() if new_sentence else []
            
            return new_sentence, display, gr.update(choices=word_choices, value=None), *[gr.update(value=p) for p in predictions]

        def clear_sentence():
            """Clear the sentence."""
            predictions = get_predictions("")
            while len(predictions) < 16:
                predictions.append("—")
            return "", update_sentence_display(""), *[gr.update(value=p) for p in predictions]

        def backspace_sentence(current_sentence: str):
            """Remove last word from sentence."""
            words = current_sentence.strip().split()
            if words:
                words.pop()
            new_sentence = " ".join(words)
            
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            while len(predictions) < 16:
                predictions.append("—")
            
            return new_sentence, display, *[gr.update(value=p) for p in predictions]

        def get_category_words(category: str, current_sentence: str, gender: str = "male"):
            """Get words for a specific category."""
            from .aac_keyboard import get_words_for_gender
            
            HEBREW_WORDS = get_words_for_gender(gender)
            
            category_map = {
                "הכל": None,
                "כינויים": "pronouns",
                "פעלים": "verbs",
                "שאלות": "questions",
                "בסיסי": "basic",
                "אוכל": "food",
                "רגשות": "feelings",
                "פעולות": "actions",
                "מקומות": "places",
                "זמן": "time",
                "אנשים": "people",
                "תארים": "adjectives",
                "גוף": "body",
                "מזג אוויר": "weather",
                "מספרים": "numbers",
                "צבעים": "colors",
                "יומיום": "daily",
                "משפחה": "family",
                "פיננסים": "finance",
                "קניות": "shopping",
                "רפואה": "medical",
                "תחבורה": "transportation",
                "בית": "home",
                "תקשורת": "communication",
                "בגדים": "clothing",
                "בקשות": "requests",
                "עבודה": "work",
                "טכנולוגיה": "technology",
                "בילוי": "entertainment",
                "חירום": "emergency",
                "שאלות מוכנות": "context_questions",
            }
            
            cat_key = category_map.get(category)
            if cat_key and cat_key in HEBREW_WORDS:
                words = HEBREW_WORDS[cat_key][:16]
            else:
                words = get_predictions(current_sentence)
            
            while len(words) < 16:
                words.append("—")
            
            return [gr.update(value=w) for w in words[:16]]

        def add_typed_word(typed: str, current_sentence: str):
            """Add typed word to sentence."""
            if not typed.strip():
                return current_sentence, update_sentence_display(current_sentence), "", *[gr.update() for _ in range(16)]
            
            new_sentence = current_sentence + " " + typed.strip() if current_sentence else typed.strip()
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            while len(predictions) < 16:
                predictions.append("—")
            
            return new_sentence, display, "", *[gr.update(value=p) for p in predictions]

        def speak_sentence(sentence: str):
            """Speak the sentence using TTS."""
            if not sentence.strip():
                return None
            
            try:
                import tempfile
                import httpx
                
                # Use synchronous HTTP call - slower speed for AAC
                response = httpx.post(
                    "http://localhost:8880/v1/audio/speech",
                    json={
                        "model": "phonikud",
                        "input": sentence,
                        "voice": "piper_shaul",
                        "engine": "piper",
                        "speed": 0.75,
                        "volume_factor": 2.0,
                    },
                    timeout=60.0,
                )
                
                if response.status_code == 200:
                    audio_bytes = response.content
                    
                    temp_dir = tempfile.gettempdir()
                    temp_path = os.path.join(temp_dir, "phonikud_aac_output.wav")
                    with open(temp_path, "wb") as f:
                        f.write(audio_bytes)
                    
                    return temp_path
                else:
                    print(f"TTS error: {response.status_code} - {response.text}")
                    return None
            except Exception as e:
                print(f"Error speaking: {e}")
                import traceback
                traceback.print_exc()
                return None

        def speak_word(word: str):
            """Speak a single word using TTS."""
            if not word or word == "—":
                return None
            
            try:
                import tempfile
                import httpx
                
                # Faster speed for speak mode - short words slightly slower for clarity
                # Long words should be at normal/fast speed
                speed = 0.9 if len(word) <= 3 else 1.0
                
                response = httpx.post(
                    "http://localhost:8880/v1/audio/speech",
                    json={
                        "model": "phonikud",
                        "input": word,
                        "voice": "piper_shaul",
                        "engine": "piper",
                        "speed": speed,
                        "volume_factor": 2.0,
                    },
                    timeout=60.0,
                )
                
                if response.status_code == 200:
                    audio_bytes = response.content
                    temp_dir = tempfile.gettempdir()
                    temp_path = os.path.join(temp_dir, "phonikud_word_output.wav")
                    with open(temp_path, "wb") as f:
                        f.write(audio_bytes)
                    return temp_path
                else:
                    print(f"TTS error: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error speaking word: {e}")
                return None

        def toggle_speak_mode(current_mode: bool):
            """Toggle speak mode on/off."""
            new_mode = not current_mode
            if new_mode:
                return new_mode, gr.update(value="כפתורי שמע: דלוק", variant="primary")
            else:
                return new_mode, gr.update(value="כפתורי שמע: כבוי", variant="secondary")

        # Gender-specific quick phrases (defined inside create_interface so they're accessible)
        quick_phrases_male_ref = [
            "שלום", "תודה", "בבקשה", "סליחה", "כן", "לא",
            "עזרה", "אני רוצה", "אני צריך", "מה קורה", "בסדר", "לא בסדר",
            "מים", "אוכל", "שירותים", "כואב", "עייף", "רעב",
            "איפה זה?", "כמה עולה?", "מתי?", "למה?", "איך?", "מי?"
        ]
        quick_phrases_female_ref = [
            "שלום", "תודה", "בבקשה", "סליחה", "כן", "לא",
            "עזרה", "אני רוצה", "אני צריכה", "מה קורה", "בסדר", "לא בסדר",
            "מים", "אוכל", "שירותים", "כואב", "עייפה", "רעבה",
            "איפה זה?", "כמה עולה?", "מתי?", "למה?", "איך?", "מי?"
        ]
        
        def toggle_gender(current_gender: str):
            """Toggle between male and female - updates UI elements."""
            new_gender = "female" if current_gender == "male" else "male"
            
            # Get the appropriate button label
            if new_gender == "female":
                gender_btn_update = gr.update(value="נקבה", variant="primary")
            else:
                gender_btn_update = gr.update(value="זכר", variant="secondary")
            
            # Update the 16 prediction buttons with gender-appropriate words
            predictions = get_predictions_for_gender("", new_gender)
            while len(predictions) < 16:
                predictions.append("—")
            prediction_updates = [gr.update(value=p) for p in predictions[:16]]
            
            return [new_gender, gender_btn_update] + prediction_updates
        
        def get_predictions_for_gender(current_sentence: str, gender: str):
            """Get word predictions based on gender."""
            from .aac_keyboard import get_words_for_gender, NEXT_WORD_PATTERNS
            
            HEBREW_WORDS = get_words_for_gender(gender)
            
            predictions = []
            
            # Get context-based predictions from last word
            if current_sentence:
                words = current_sentence.strip().split()
                if words:
                    last_word = words[-1]
                    if last_word in NEXT_WORD_PATTERNS:
                        context_preds = NEXT_WORD_PATTERNS[last_word]
                        for word in context_preds:
                            if word not in predictions:
                                predictions.append(word)
            
            # Add common words from the gender-appropriate word set
            if len(predictions) < 16:
                # Get words from common categories
                common_categories = ["pronouns", "verbs", "basic", "questions"]
                for cat in common_categories:
                    if cat in HEBREW_WORDS:
                        for word in HEBREW_WORDS[cat]:
                            if word not in predictions and len(predictions) < 16:
                                predictions.append(word)
            
            return predictions

        def get_voice_for_gender(gender: str) -> str:
            """Get the voice ID for the specified gender."""
            # Currently only male voice (shaul) is available
            # When female voice is added, return appropriate voice ID
            if gender == "female":
                # Use higher pitch simulation via speed adjustment for now
                return "piper_shaul"  # Will be replaced with female voice when available
            return "piper_shaul"

        def handle_word_click(word: str, current_sentence: str, speak_mode: bool, gender: str = "male"):
            """Handle word button click - either add to sentence or speak it."""
            if word == "—":
                if speak_mode:
                    return current_sentence, update_sentence_display(current_sentence), None, *[gr.update() for _ in range(16)]
                return current_sentence, update_sentence_display(current_sentence), *[gr.update() for _ in range(16)]
            
            if speak_mode:
                # Speak the word without adding to sentence
                audio_path = speak_word(word)
                return current_sentence, update_sentence_display(current_sentence), audio_path, *[gr.update() for _ in range(16)]
            else:
                # Add word to sentence
                if current_sentence:
                    new_sentence = current_sentence + " " + word
                else:
                    new_sentence = word
                
                display = update_sentence_display(new_sentence)
                predictions = get_predictions(new_sentence)
                while len(predictions) < 16:
                    predictions.append("—")
                
                return new_sentence, display, None, *[gr.update(value=p) for p in predictions]
        
        # Ready answers data - organized by category with gender support
        READY_ANSWERS_MALE = {
            "ברכות": ["שלום!", "בוקר טוב!", "צהריים טובים!", "ערב טוב!", "לילה טוב!", "מה נשמע?", "איך אתה?", "איך את?", "נעים להכיר", "להתראות!", "יום טוב!", "סוף שבוע נעים"],
            "תגובות": ["כן, בבקשה", "לא, תודה", "בסדר גמור", "בטח!", "אולי", "אני מסכים", "אני לא מסכים", "תודה רבה!", "תודה על העזרה", "סליחה, לא הבנתי", "רגע בבקשה", "זה בסדר"],
            "עזרה": ["אפשר לקבל עזרה?", "תוכל לעזור לי?", "תוכלי לעזור לי?", "אני צריך עזרה", "אני לא מצליח", "זה לא עובד", "איך עושים את זה?", "תסביר לי בבקשה", "אפשר לשאול שאלה?", "יש לי בעיה", "משהו לא בסדר", "אני צריך משהו"],
            "צרכים": ["אני רוצה לשתות", "אני רוצה לאכול", "אני צמא", "אני רעב", "אני צריך מים", "אני רוצה קפה", "אני רוצה תה", "אני צריך לנוח", "אני עייף", "אני רוצה לישון", "אני רוצה לצאת", "אני רוצה ללכת הביתה"],
            "הרגשות": ["טוב לי", "לא טוב לי", "אני שמח", "אני עצוב", "אני כועס", "אני עייף מאוד", "אני לחוץ", "אני דואג", "אני פוחד", "אני רגוע", "כואב לי", "אני חולה"],
            "שאלות": ["מה השעה?", "איפה השירותים?", "מתי זה מתחיל?", "מתי זה נגמר?", "כמה זה עולה?", "איפה זה נמצא?", "לאן הולכים?", "מי זה?", "מה זה?", "למה?", "איך מגיעים ל...?", "כמה זמן זה לוקח?"],
            "חברה": ["מה אתה חושב?", "מה דעתך?", "אני מסכים איתך", "יפה אמרת", "זה נכון", "זה לא נכון", "ספר לי עוד", "מעניין!", "מצחיק!", "חבל", "נכון מאוד", "אני מבין"],
            "מקומות": ["אני רוצה ללכת ל...", "איפה היציאה?", "איפה הכניסה?", "אני צריך להגיע ל...", "איך מגיעים לשם?", "זה רחוק?", "אני הולך לשירותים", "אני חוזר עכשיו", "תחכה לי רגע", "אני יוצא החוצה", "—", "—"],
            "יומיום": ["אני רוצה לראות טלוויזיה", "אני רוצה לשחק", "אני רוצה לקרוא", "אני רוצה לשמוע מוזיקה", "אני רוצה לגלוש באינטרנט", "אני רוצה לדבר עם...", "תתקשר לי ל...", "אני רוצה ללמוד", "אני רוצה לעבוד", "אני רוצה לנוח", "—", "—"],
            "אוכל": ["בתיאבון!", "היה טעים", "תודה על האוכל", "אני רוצה עוד", "אני שבע", "זה טעים!", "זה לא טעים", "אני לא אוהב את זה", "מה יש לאכול?", "מתי האוכל?", "אני רוצה משהו מתוק", "אני רוצה שתייה קרה"],
            "רפואי": ["אני לא מרגיש טוב", "כואב לי פה", "אני צריך רופא", "תביאו לי תרופה", "אני צריך לשכב", "תקראו לעזרה", "זה מכאיב לי", "אני מרגיש חולשה", "אני צריך מנוחה", "תביאו לי מים", "—", "—"],
            "מזג אוויר": ["חם לי", "קר לי", "נעים פה", "אני רוצה מזגן", "אני רוצה חימום", "פתחו חלון", "סגרו חלון", "מה מזג האוויר?", "יש שמש?", "ירד גשם?", "—", "—"],
            "תקשורת": ["תתקשר לי", "שלח לי הודעה", "אני רוצה לדבר בטלפון", "תענה לטלפון", "מי צלצל?", "יש לי הודעה?", "תשלח וואטסאפ", "אני רוצה לשלוח תמונה", "תצלם אותי", "אני רוצה לראות וידאו", "—", "—"],
            "קניות": ["כמה זה?", "זה יקר מדי", "בבקשה קבלה", "אני רוצה לקנות", "יש הנחה?", "אני משלם במזומן", "אני משלם באשראי", "איפה הקופה?", "תעטוף לי את זה", "תודה, לא צריך", "—", "—"],
            "עבודה": ["יש לי פגישה", "אני עסוק", "תזכיר לי", "אני צריך לסיים", "מתי ההפסקה?", "אני גמרתי", "זה מוכן", "עוד רגע", "אני באמצע", "תחכה שאסיים", "—", "—"],
            "תחביבים": ["אני רוצה לצייר", "אני רוצה לנגן", "אני רוצה לרקוד", "אני רוצה לשחק משחק", "אני רוצה לקרוא ספר", "אני אוהב מוזיקה", "אני רוצה לכתוב", "אני רוצה לבשל", "אני רוצה לצלם", "אני רוצה לטייל", "—", "—"],
            "טבע": ["אני רוצה לטייל בטבע", "יפה פה", "הפרחים יפים", "העצים ירוקים", "אני אוהב חיות", "יש ציפורים", "הים יפה", "ההרים גבוהים", "אני רוצה לשבת בחוץ", "אוויר צח", "—", "—"],
            "ספורט": ["אני רוצה לשחק כדורגל", "אני רוצה לשחק כדורסל", "אני רוצה לשחות", "אני רוצה לרוץ", "אני רוצה ללכת למכון כושר", "מי מנצח?", "זה משחק טוב!", "אני אוהב ספורט", "אני עייף מהאימון", "—", "—", "—"],
            "משפחה": ["איפה אמא?", "איפה אבא?", "אני רוצה לדבר עם...", "תודה למשפחה", "אני אוהב אותך", "אני אוהבת אותך", "מתי באים הילדים?", "סבא וסבתא", "אחים ואחיות", "דודים ודודות", "—", "—"],
        }
        
        READY_ANSWERS_FEMALE = {
            "ברכות": ["שלום!", "בוקר טוב!", "צהריים טובים!", "ערב טוב!", "לילה טוב!", "מה נשמע?", "איך אתה?", "איך את?", "נעים להכיר", "להתראות!", "יום טוב!", "סוף שבוע נעים"],
            "תגובות": ["כן, בבקשה", "לא, תודה", "בסדר גמור", "בטח!", "אולי", "אני מסכימה", "אני לא מסכימה", "תודה רבה!", "תודה על העזרה", "סליחה, לא הבנתי", "רגע בבקשה", "זה בסדר"],
            "עזרה": ["אפשר לקבל עזרה?", "תוכל לעזור לי?", "תוכלי לעזור לי?", "אני צריכה עזרה", "אני לא מצליחה", "זה לא עובד", "איך עושים את זה?", "תסבירי לי בבקשה", "אפשר לשאול שאלה?", "יש לי בעיה", "משהו לא בסדר", "אני צריכה משהו"],
            "צרכים": ["אני רוצה לשתות", "אני רוצה לאכול", "אני צמאה", "אני רעבה", "אני צריכה מים", "אני רוצה קפה", "אני רוצה תה", "אני צריכה לנוח", "אני עייפה", "אני רוצה לישון", "אני רוצה לצאת", "אני רוצה ללכת הביתה"],
            "הרגשות": ["טוב לי", "לא טוב לי", "אני שמחה", "אני עצובה", "אני כועסת", "אני עייפה מאוד", "אני לחוצה", "אני דואגת", "אני פוחדת", "אני רגועה", "כואב לי", "אני חולה"],
            "שאלות": ["מה השעה?", "איפה השירותים?", "מתי זה מתחיל?", "מתי זה נגמר?", "כמה זה עולה?", "איפה זה נמצא?", "לאן הולכים?", "מי זה?", "מה זה?", "למה?", "איך מגיעים ל...?", "כמה זמן זה לוקח?"],
            "חברה": ["מה אתה חושב?", "מה דעתך?", "אני מסכימה איתך", "יפה אמרת", "זה נכון", "זה לא נכון", "ספרי לי עוד", "מעניין!", "מצחיק!", "חבל", "נכון מאוד", "אני מבינה"],
            "מקומות": ["אני רוצה ללכת ל...", "איפה היציאה?", "איפה הכניסה?", "אני צריכה להגיע ל...", "איך מגיעים לשם?", "זה רחוק?", "אני הולכת לשירותים", "אני חוזרת עכשיו", "תחכי לי רגע", "אני יוצאת החוצה", "—", "—"],
            "יומיום": ["אני רוצה לראות טלוויזיה", "אני רוצה לשחק", "אני רוצה לקרוא", "אני רוצה לשמוע מוזיקה", "אני רוצה לגלוש באינטרנט", "אני רוצה לדבר עם...", "תתקשרי לי ל...", "אני רוצה ללמוד", "אני רוצה לעבוד", "אני רוצה לנוח", "—", "—"],
            "אוכל": ["בתיאבון!", "היה טעים", "תודה על האוכל", "אני רוצה עוד", "אני שבעה", "זה טעים!", "זה לא טעים", "אני לא אוהבת את זה", "מה יש לאכול?", "מתי האוכל?", "אני רוצה משהו מתוק", "אני רוצה שתייה קרה"],
            "רפואי": ["אני לא מרגישה טוב", "כואב לי פה", "אני צריכה רופא", "תביאו לי תרופה", "אני צריכה לשכב", "תקראו לעזרה", "זה מכאיב לי", "אני מרגישה חולשה", "אני צריכה מנוחה", "תביאו לי מים", "—", "—"],
            "מזג אוויר": ["חם לי", "קר לי", "נעים פה", "אני רוצה מזגן", "אני רוצה חימום", "פתחו חלון", "סגרו חלון", "מה מזג האוויר?", "יש שמש?", "ירד גשם?", "—", "—"],
            "תקשורת": ["תתקשרי לי", "שלחי לי הודעה", "אני רוצה לדבר בטלפון", "תעני לטלפון", "מי צלצל?", "יש לי הודעה?", "תשלחי וואטסאפ", "אני רוצה לשלוח תמונה", "תצלמי אותי", "אני רוצה לראות וידאו", "—", "—"],
            "קניות": ["כמה זה?", "זה יקר מדי", "בבקשה קבלה", "אני רוצה לקנות", "יש הנחה?", "אני משלמת במזומן", "אני משלמת באשראי", "איפה הקופה?", "תעטפי לי את זה", "תודה, לא צריך", "—", "—"],
            "עבודה": ["יש לי פגישה", "אני עסוקה", "תזכירי לי", "אני צריכה לסיים", "מתי ההפסקה?", "אני גמרתי", "זה מוכן", "עוד רגע", "אני באמצע", "תחכי שאסיים", "—", "—"],
            "תחביבים": ["אני רוצה לצייר", "אני רוצה לנגן", "אני רוצה לרקוד", "אני רוצה לשחק משחק", "אני רוצה לקרוא ספר", "אני אוהבת מוזיקה", "אני רוצה לכתוב", "אני רוצה לבשל", "אני רוצה לצלם", "אני רוצה לטייל", "—", "—"],
            "טבע": ["אני רוצה לטייל בטבע", "יפה פה", "הפרחים יפים", "העצים ירוקים", "אני אוהבת חיות", "יש ציפורים", "הים יפה", "ההרים גבוהים", "אני רוצה לשבת בחוץ", "אוויר צח", "—", "—"],
            "ספורט": ["אני רוצה לשחק כדורגל", "אני רוצה לשחק כדורסל", "אני רוצה לשחות", "אני רוצה לרוץ", "אני רוצה ללכת למכון כושר", "מי מנצח?", "זה משחק טוב!", "אני אוהבת ספורט", "אני עייפה מהאימון", "—", "—", "—"],
            "משפחה": ["איפה אמא?", "איפה אבא?", "אני רוצה לדבר עם...", "תודה למשפחה", "אני אוהב אותך", "אני אוהבת אותך", "מתי באים הילדים?", "סבא וסבתא", "אחים ואחיות", "דודים ודודות", "—", "—"],
        }
        
        def get_ready_answers_for_category(category_label: str, gender: str = "male") -> list:
            """Get ready answers for a category based on gender."""
            if gender == "female":
                answers = READY_ANSWERS_FEMALE.get(category_label, READY_ANSWERS_FEMALE.get("ברכות", []))
            else:
                answers = READY_ANSWERS_MALE.get(category_label, READY_ANSWERS_MALE.get("ברכות", []))
            # Pad to 12 buttons
            while len(answers) < 12:
                answers.append("—")
            return answers[:12]
        
        def handle_ready_answer_category_click(category_label: str, gender: str = "male"):
            """Handle ready answer category button click - update the answer buttons based on gender."""
            answers = get_ready_answers_for_category(category_label, gender)
            return [gr.update(value=a) for a in answers]
        
        def handle_ready_answer_click(answer: str, current_sentence: str, speak_mode: bool):
            """Handle ready answer button click - add phrase to sentence."""
            if answer == "—":
                if speak_mode:
                    return current_sentence, update_sentence_display(current_sentence), None, *[gr.update() for _ in range(16)]
                return current_sentence, update_sentence_display(current_sentence), *[gr.update() for _ in range(16)]
            
            if speak_mode:
                # Speak the phrase without adding to sentence
                audio_path = speak_word(answer)
                return current_sentence, update_sentence_display(current_sentence), audio_path, *[gr.update() for _ in range(16)]
            else:
                # Add phrase to sentence
                if current_sentence:
                    new_sentence = current_sentence + " " + answer
                else:
                    new_sentence = answer
                
                display = update_sentence_display(new_sentence)
                predictions = get_predictions(new_sentence)
                while len(predictions) < 16:
                    predictions.append("—")
                
                return new_sentence, display, None, *[gr.update(value=p) for p in predictions]
        
        # New feature handlers
        def add_punctuation(punct: str, current_sentence: str):
            """Add punctuation to sentence."""
            if punct == "—":
                return current_sentence, update_sentence_display(current_sentence), *[gr.update() for _ in range(16)]
            
            # Add punctuation directly (no space before punctuation)
            if current_sentence:
                new_sentence = current_sentence + punct
            else:
                new_sentence = punct
            
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            while len(predictions) < 16:
                predictions.append("—")
            
            return new_sentence, display, *[gr.update(value=p) for p in predictions]
        
        def add_custom_text(text: str, current_sentence: str):
            """Add custom typed text to sentence."""
            if not text.strip():
                return current_sentence, update_sentence_display(current_sentence), "", *[gr.update() for _ in range(16)]
            
            if current_sentence:
                new_sentence = current_sentence + " " + text.strip()
            else:
                new_sentence = text.strip()
            
            display = update_sentence_display(new_sentence)
            predictions = get_predictions(new_sentence)
            while len(predictions) < 16:
                predictions.append("—")
            
            return new_sentence, display, "", *[gr.update(value=p) for p in predictions]
        
        def copy_to_clipboard(current_sentence: str):
            """Copy sentence to clipboard - returns JavaScript to execute."""
            if not current_sentence:
                return gr.HTML(value="<script>showCopyNotification('אין טקסט להעתקה');</script>")
            return gr.HTML(value=f"""
                <script>
                (function() {{
                    navigator.clipboard.writeText('{current_sentence}').then(() => {{
                        const notif = document.createElement('div');
                        notif.className = 'copy-notification';
                        notif.textContent = 'הועתק!';
                        document.body.appendChild(notif);
                        setTimeout(() => notif.remove(), 2000);
                    }}).catch(() => {{
                        const notif = document.createElement('div');
                        notif.className = 'copy-notification';
                        notif.textContent = 'שגיאה בהעתקה';
                        document.body.appendChild(notif);
                        setTimeout(() => notif.remove(), 2000);
                    }});
                }})();
                </script>
            """)
        
        def save_favorite(current_sentence: str, current_favorites: list):
            """Save current sentence to favorites."""
            if not current_sentence or current_sentence in current_favorites:
                return current_favorites, *[gr.update() for _ in range(8)]
            
            new_favorites = current_favorites + [current_sentence]
            # Keep only last 8 favorites
            if len(new_favorites) > 8:
                new_favorites = new_favorites[-8:]
            
            # Update favorite buttons
            updates = []
            for i in range(8):
                if i < len(new_favorites):
                    updates.append(gr.update(value=new_favorites[i]))
                else:
                    updates.append(gr.update(value="—"))
            
            return new_favorites, *updates
        
        def clear_favorites():
            """Clear all favorites."""
            return [], *[gr.update(value="—") for _ in range(8)]
        
        def handle_favorite_click(favorite: str, current_sentence: str):
            """Handle favorite button click - replace or add to sentence."""
            if favorite == "—":
                return current_sentence, update_sentence_display(current_sentence), *[gr.update() for _ in range(16)]
            
            # Replace sentence with favorite
            display = update_sentence_display(favorite)
            predictions = get_predictions(favorite)
            while len(predictions) < 16:
                predictions.append("—")
            
            return favorite, display, *[gr.update(value=p) for p in predictions]
        
        def speak_sentence_with_speed(sentence: str, speed: float):
            """Speak the sentence using TTS with custom speed."""
            if not sentence.strip():
                return None
            
            try:
                import tempfile
                import httpx
                
                response = httpx.post(
                    "http://localhost:8880/v1/audio/speech",
                    json={
                        "model": "phonikud",
                        "input": sentence,
                        "voice": "piper_shaul",
                        "engine": "piper",
                        "speed": speed,
                        "volume_factor": 2.0,
                    },
                    timeout=60.0,
                )
                
                if response.status_code == 200:
                    audio_bytes = response.content
                    temp_dir = tempfile.gettempdir()
                    temp_path = os.path.join(temp_dir, "phonikud_aac_output.wav")
                    with open(temp_path, "wb") as f:
                        f.write(audio_bytes)
                    return temp_path
                else:
                    print(f"TTS error: {response.status_code} - {response.text}")
                    return None
            except Exception as e:
                print(f"Error speaking: {e}")
                import traceback
                traceback.print_exc()
                return None

        # Wire up TTS events
        phonemize_btn.click(
            fn=phonemize_handler,
            inputs=[text_input],
            outputs=[phoneme_output],
        )

        generate_btn.click(
            fn=generate_handler,
            inputs=[text_input, voice_dropdown, engine_dropdown, speed_slider, volume_slider],
            outputs=[audio_output, vocalized_output, info_output],
        )

        generate_with_phonemes_btn.click(
            fn=generate_with_phonemes_handler,
            inputs=[text_input, voice_dropdown, engine_dropdown, speed_slider, volume_slider],
            outputs=[phoneme_output, audio_output, vocalized_output, info_output],
        )

        # Periodic status check
        timer = gr.Timer(value=5)
        timer.tick(
            fn=update_status,
            outputs=[status_btn, voice_dropdown, timer],
        )

        # Wire up speak mode toggle
        speak_mode_btn.click(
            fn=toggle_speak_mode,
            inputs=[speak_mode_state],
            outputs=[speak_mode_state, speak_mode_btn],
        )

        # Wire up gender toggle - updates prediction buttons
        gender_btn.click(
            fn=toggle_gender,
            inputs=[gender_state],
            outputs=[gender_state, gender_btn] + prediction_btns,
        )

        # Wire up AAC events with speak mode support
        for btn in prediction_btns:
            btn.click(
                fn=handle_word_click,
                inputs=[btn, sentence_state, speak_mode_state],
                outputs=[sentence_state, sentence_display, aac_audio_output] + prediction_btns,
            )

        # Wire up most used buttons
        for btn in most_used_btns:
            btn.click(
                fn=handle_word_click,
                inputs=[btn, sentence_state, speak_mode_state],
                outputs=[sentence_state, sentence_display, aac_audio_output] + prediction_btns,
            )

        # Wire up question and connector buttons
        for btn in question_connector_btns:
            btn.click(
                fn=handle_word_click,
                inputs=[btn, sentence_state, speak_mode_state],
                outputs=[sentence_state, sentence_display, aac_audio_output] + prediction_btns,
            )

        # Wire up basic words buttons
        for btn in basic_words_btns:
            btn.click(
                fn=handle_word_click,
                inputs=[btn, sentence_state, speak_mode_state],
                outputs=[sentence_state, sentence_display, aac_audio_output] + prediction_btns,
            )

        # Wire up function words buttons
        for btn in function_words_btns:
            btn.click(
                fn=handle_word_click,
                inputs=[btn, sentence_state, speak_mode_state],
                outputs=[sentence_state, sentence_display, aac_audio_output] + prediction_btns,
            )

        clear_btn.click(
            fn=clear_sentence,
            outputs=[sentence_state, sentence_display] + prediction_btns,
        )

        backspace_btn.click(
            fn=backspace_sentence,
            inputs=[sentence_state],
            outputs=[sentence_state, sentence_display] + prediction_btns,
        )

        # Wire up category button events
        def create_category_handler(category_name):
            def handler(current_sentence, gender):
                return get_category_words(category_name, current_sentence, gender)
            return handler
        
        all_categories = category_row1 + category_row2 + category_row3 + category_row4 + category_row5
        for i, btn in enumerate(category_btns):
            if i < len(all_categories):
                btn.click(
                    fn=create_category_handler(all_categories[i]),
                    inputs=[sentence_state, gender_state],
                    outputs=prediction_btns,
                )

        speak_btn.click(
            fn=speak_sentence,
            inputs=[sentence_state],
            outputs=[aac_audio_output],
        )

        # Wire up hidden word removal button (for click-to-remove on sentence words)
        remove_word_btn.click(
            fn=remove_word_at_index,
            inputs=[sentence_state, selected_word_index],
            outputs=[sentence_state, sentence_display, selected_word_index] + prediction_btns,
        )

        # Wire up ready answer category buttons
        all_ready_cats = ready_cat_row1 + ready_cat_row2 + ready_cat_row3
        for i, btn in enumerate(ready_answer_category_btns):
            if i < len(all_ready_cats):
                btn.click(
                    fn=handle_ready_answer_category_click,
                    inputs=[btn, gender_state],
                    outputs=ready_answer_btns,
                )

        # Wire up ready answer buttons
        for btn in ready_answer_btns:
            btn.click(
                fn=handle_ready_answer_click,
                inputs=[btn, sentence_state, speak_mode_state],
                outputs=[sentence_state, sentence_display, aac_audio_output] + prediction_btns,
            )

        # Wire up copy button
        copy_btn.click(
            fn=copy_to_clipboard,
            inputs=[sentence_state],
            outputs=[gr.HTML()],
        )

        # Wire up custom text input
        add_custom_text_btn.click(
            fn=add_custom_text,
            inputs=[custom_text_input, sentence_state],
            outputs=[sentence_state, sentence_display, custom_text_input] + prediction_btns,
        )

        # Wire up punctuation buttons
        for btn in punctuation_btns:
            btn.click(
                fn=add_punctuation,
                inputs=[btn, sentence_state],
                outputs=[sentence_state, sentence_display] + prediction_btns,
            )

        # Wire up favorites
        save_favorite_btn.click(
            fn=save_favorite,
            inputs=[sentence_state, favorites_state],
            outputs=[favorites_state] + favorites_btns,
        )

        clear_favorites_btn.click(
            fn=clear_favorites,
            outputs=[favorites_state] + favorites_btns,
        )

        for btn in favorites_btns:
            btn.click(
                fn=handle_favorite_click,
                inputs=[btn, sentence_state],
                outputs=[sentence_state, sentence_display] + prediction_btns,
            )

        # Wire up speak button with speed control
        speak_btn.click(
            fn=speak_sentence_with_speed,
            inputs=[sentence_state, aac_speed_slider],
            outputs=[aac_audio_output],
        )

    return demo
