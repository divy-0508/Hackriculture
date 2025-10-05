// Simple client-side translations for EN and HI (India-centric).
const TRANSLATIONS = {
  en: {
    hero_title: "Hackriculture",
    hero_sub: "AI tools for small farmers — yield prediction & irrigation recommendations.",
    get_started: "Get Started",
    learn_more: "Learn more",
    card_yield: "Crop Yield Predictor",
    card_yield_desc: "Enter soil & crop info, and get yield estimates using our ML model.",
    card_irrig: "Irrigation Recommendation",
    card_irrig_desc: "Quick advice on whether irrigation is needed (Rice-focused).",
    about_heading: "About Hackriculture",
    about_text: "Hackriculture helps small-scale farmers make data-driven decisions.",
    services_heading: "Services",
    services_text: "We provide two core services to support small farmers:",
    yield_form_title: "Crop Yield Predictor",
    predict: "Predict Yield",
    irrigation_title: "Irrigation Recommendation",
    check_irrig: "Check",
    result: "Result",
    prediction_result: "Prediction",
    loc_hint: "used to fetch Temperature, Humidity & Wind",
    home: "Home",
    about: "About",
    services: "Services",
    yield: "Yield",
    irrigation: "Irrigation"
  },
  hi: {
    hero_title: "हैककृर्षि",
    hero_sub: "छोटे किसानों के लिए एआई उपकरण — उपज अनुमान और सिंचाई सिफारिशें।",
    get_started: "शुरू करें",
    learn_more: "और पढ़ें",
    card_yield: "फसल उपज भविष्यवक्ता",
    card_yield_desc: "मिट्टी और फसल जानकारी दर्ज करें और मॉडल से उपज अनुमान प्राप्त करें।",
    card_irrig: "सिंचाई सिफारिश",
    card_irrig_desc: "क्या सिंचाई आवश्यक है इसकी त्वरित सलाह (केंद्रित: चावल)।",
    about_heading: "हमारे बारे में",
    about_text: "Hackriculture छोटे किसानों को डेटा-आधारित निर्णय लेने में मदद करता है।",
    services_heading: "सेवाएँ",
    services_text: "हम छोटे किसानों के लिए दो मुख्य सेवाएँ प्रदान करते हैं:",
    yield_form_title: "फसल उपज भविष्यवक्ता",
    predict: "उपज का अनुमान लगाएँ",
    irrigation_title: "सिंचाई सिफारिश",
    check_irrig: "जांचें",
    result: "परिणाम",
    prediction_result: "अनुमान",
    loc_hint: "— तापमान, आद्रता और हवा प्राप्त करने के लिए प्रयोग करें",
    home: "होम",
    about: "हमारे बारे में",
    services: "सेवाएँ",
    yield: "उपज",
    irrigation: "सिंचाई"
  }
};

function applyTranslations(lang){
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    const key = el.getAttribute('data-i18n');
    if(TRANSLATIONS[lang] && TRANSLATIONS[lang][key]){
      el.innerText = TRANSLATIONS[lang][key];
    }
  });
  // keep placeholders and inputs unchanged, but you can localize them as well
}

document.addEventListener("DOMContentLoaded", function(){
  // Language
  const ls = localStorage.getItem('hack_lang') || 'en';
  const langSelect = document.getElementById('langSwitch');
  if(langSelect) { langSelect.value = ls; }
  applyTranslations(ls);

  if(langSelect){
    langSelect.addEventListener('change', (e)=>{
      const v = e.target.value;
      localStorage.setItem('hack_lang', v);
      applyTranslations(v);
    });
  }

  // Theme toggle
  const themeBtn = document.getElementById('themeToggle');
  const body = document.body;
  let theme = localStorage.getItem('hack_theme') || 'light';
  body.className = theme;
  if(themeBtn){
    themeBtn.addEventListener('click', ()=>{
      theme = (body.className === 'light') ? 'dark' : 'light';
      body.className = theme;
      localStorage.setItem('hack_theme', theme);
      themeBtn.innerText = theme === 'dark' ? '☀️' : '🌙';
    });
    themeBtn.innerText = body.className === 'dark' ? '☀️' : '🌙';
  }

  // Parallax effect on scroll (gentle)
  const parallax = document.querySelector('.parallax');
  window.addEventListener('scroll', ()=>{
    if(parallax){
      const y = window.scrollY;
      parallax.style.backgroundPosition = `center ${-y*0.1}px`;
    }
  });

  // Fetch weather button on yield form
  const fetchBtn = document.getElementById('fetchWeather');
  if(fetchBtn){
    fetchBtn.addEventListener('click', async ()=>{
      const loc = document.getElementById('locationInput').value;
      if(!loc) { alert('Enter a city name'); return; }
      fetchBtn.disabled = true; fetchBtn.innerText = 'Fetching...';
      try {
        const resp = await fetch('/get_weather', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({location: loc})
        });
        const j = await resp.json();
        if(resp.ok){
          document.getElementById('Temperature').value = j.temperature ?? '';
          document.getElementById('Humidity').value = j.humidity ?? '';
          document.getElementById('Wind_Speed').value = j.wind_speed ?? '';
        } else {
          alert("Weather error: " + (j.error || 'unknown'));
        }
      } catch (e) {
        alert('Error: ' + e.message);
      }
      fetchBtn.disabled = false; fetchBtn.innerText = 'Fetch weather';
    });
  }
});
