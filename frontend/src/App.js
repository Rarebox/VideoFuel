import React, { useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [language, setLanguage] = useState("en");
  const [model, setModel] = useState("deephermes2pro");
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  
  // Form states
  const [topic, setTopic] = useState("");
  const [selectedTitle, setSelectedTitle] = useState("");
  const [videoLength, setVideoLength] = useState(5);
  
  // Results states
  const [titles, setTitles] = useState([]);
  const [description, setDescription] = useState("");
  const [hashtags, setHashtags] = useState([]);
  const [script, setScript] = useState(null);
  const [thumbnailTexts, setThumbnailTexts] = useState([]);
  const [seoScores, setSeoScores] = useState(null);
  
  // API calls
  const generateTitles = async () => {
    if (!topic.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/generate-titles`, {
        topic,
        language,
        model
      });
      setTitles(response.data.titles);
      setCurrentStep(2);
    } catch (error) {
      console.error("Error generating titles:", error);
      alert("Error generating titles. Please try again.");
    }
    setIsLoading(false);
  };

  const generateDescription = async () => {
    if (!selectedTitle) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/generate-description`, {
        title: selectedTitle,
        language,
        model
      });
      setDescription(response.data.description);
      setHashtags(response.data.hashtags);
      setCurrentStep(3);
    } catch (error) {
      console.error("Error generating description:", error);
      alert("Error generating description. Please try again.");
    }
    setIsLoading(false);
  };

  const generateScript = async () => {
    if (!selectedTitle) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/generate-script`, {
        title: selectedTitle,
        language,
        video_length_minutes: videoLength,
        model
      });
      setScript(response.data);
      setCurrentStep(4);
    } catch (error) {
      console.error("Error generating script:", error);
      alert("Error generating script. Please try again.");
    }
    setIsLoading(false);
  };

  const generateThumbnail = async () => {
    if (!selectedTitle) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/generate-thumbnail`, {
        title: selectedTitle,
        language,
        model
      });
      setThumbnailTexts(response.data.thumbnail_texts);
      setCurrentStep(5);
    } catch (error) {
      console.error("Error generating thumbnail texts:", error);
      alert("Error generating thumbnail texts. Please try again.");
    }
    setIsLoading(false);
  };

  const analyzeSEO = async () => {
    if (!selectedTitle || !description || !hashtags.length) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/analyze-seo`, {
        title: selectedTitle,
        description,
        hashtags,
        language
      });
      setSeoScores(response.data);
      setCurrentStep(6);
    } catch (error) {
      console.error("Error analyzing SEO:", error);
      alert("Error analyzing SEO. Please try again.");
    }
    setIsLoading(false);
  };

  const resetFlow = () => {
    setCurrentStep(1);
    setTopic("");
    setSelectedTitle("");
    setTitles([]);
    setDescription("");
    setHashtags([]);
    setScript(null);
    setThumbnailTexts([]);
    setSeoScores(null);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBg = (score) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-pink-400 to-yellow-400 bg-clip-text text-transparent">
            VideoFuel AI
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            {language === "en" ? "AI Toolkit for YouTube Creators" : "YouTube İçerik Üreticileri için AI Toolkit"}
          </p>
          
          {/* Controls */}
          <div className="flex justify-center gap-6 mb-8">
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-lg p-4">
              <label className="block text-white text-sm font-bold mb-2">
                {language === "en" ? "Language" : "Dil"}
              </label>
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-white bg-opacity-20 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400"
              >
                <option value="en" className="text-black">English</option>
                <option value="tr" className="text-black">Türkçe</option>
              </select>
            </div>
            
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-lg p-4">
              <label className="block text-white text-sm font-bold mb-2">
                {language === "en" ? "AI Model" : "AI Model"}
              </label>
              <select 
                value={model} 
                onChange={(e) => setModel(e.target.value)}
                className="bg-white bg-opacity-20 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400"
              >
                <option value="deephermes2pro" className="text-black">DeepHermes 2 Pro</option>
                <option value="mixtral" className="text-black">Mixtral</option>
                <option value="gpt4o" className="text-black">GPT-4o</option>
              </select>
            </div>
          </div>
        </div>

        {/* Step Indicator */}
        <div className="flex justify-center mb-12">
          <div className="flex items-center space-x-4">
            {[1, 2, 3, 4, 5, 6].map((step) => (
              <div key={step} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                  currentStep >= step ? 'bg-pink-500 text-white' : 'bg-gray-600 text-gray-300'
                }`}>
                  {step}
                </div>
                {step < 6 && <div className={`w-8 h-1 ${currentStep > step ? 'bg-pink-500' : 'bg-gray-600'}`}></div>}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          
          {/* Step 1: Topic Input */}
          {currentStep === 1 && (
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-6">
                {language === "en" ? "1. Enter Your Video Topic" : "1. Video Konunuzu Girin"}
              </h2>
              <div className="space-y-4">
                <textarea
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder={language === "en" ? "Enter your video topic (e.g., 'how to cook pasta')" : "Video konunuzu girin (örn: 'makarna nasıl pişirilir')"}
                  className="w-full h-32 bg-white bg-opacity-20 text-white rounded-lg px-4 py-3 placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-pink-400"
                />
                <button
                  onClick={generateTitles}
                  disabled={isLoading || !topic.trim()}
                  className="w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold py-3 px-6 rounded-lg hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                >
                  {isLoading ? (language === "en" ? "Generating..." : "Üretiliyor...") : (language === "en" ? "Generate Titles" : "Başlık Üret")}
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Title Selection */}
          {currentStep === 2 && (
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-6">
                {language === "en" ? "2. Select Your Favorite Title" : "2. Favori Başlığınızı Seçin"}
              </h2>
              <div className="space-y-4">
                {titles.map((title, index) => (
                  <div 
                    key={index}
                    onClick={() => setSelectedTitle(title)}
                    className={`p-4 rounded-lg cursor-pointer transition-all duration-300 ${
                      selectedTitle === title 
                        ? 'bg-pink-500 bg-opacity-80 text-white' 
                        : 'bg-white bg-opacity-20 text-white hover:bg-opacity-30'
                    }`}
                  >
                    <div className="font-medium">{title}</div>
                    <div className="text-sm text-gray-300 mt-1">
                      {title.length} {language === "en" ? "characters" : "karakter"}
                    </div>
                  </div>
                ))}
                <div className="flex gap-4">
                  <button
                    onClick={() => setCurrentStep(1)}
                    className="flex-1 bg-gray-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-gray-700 transition-all duration-300"
                  >
                    {language === "en" ? "Back" : "Geri"}
                  </button>
                  <button
                    onClick={generateDescription}
                    disabled={!selectedTitle}
                    className="flex-1 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold py-3 px-6 rounded-lg hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                  >
                    {language === "en" ? "Next: Description" : "Sonraki: Açıklama"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Description & Hashtags */}
          {currentStep === 3 && (
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-6">
                {language === "en" ? "3. Description & Hashtags" : "3. Açıklama ve Hashtag'ler"}
              </h2>
              {description && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-bold text-white mb-3">{language === "en" ? "Description:" : "Açıklama:"}</h3>
                    <div className="bg-white bg-opacity-20 rounded-lg p-4 text-white">
                      {description}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white mb-3">{language === "en" ? "Hashtags:" : "Hashtag'ler:"}</h3>
                    <div className="flex flex-wrap gap-2">
                      {hashtags.map((hashtag, index) => (
                        <span key={index} className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">
                          {hashtag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <button
                      onClick={() => setCurrentStep(2)}
                      className="flex-1 bg-gray-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-gray-700 transition-all duration-300"
                    >
                      {language === "en" ? "Back" : "Geri"}
                    </button>
                    <button
                      onClick={() => {
                        setCurrentStep(4);
                        generateScript();
                      }}
                      className="flex-1 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold py-3 px-6 rounded-lg hover:from-pink-600 hover:to-purple-700 transition-all duration-300"
                    >
                      {language === "en" ? "Next: Script" : "Sonraki: Senaryo"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 4: Script */}
          {currentStep === 4 && (
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-6">
                {language === "en" ? "4. Video Script" : "4. Video Senaryosu"}
              </h2>
              <div className="mb-4">
                <label className="block text-white text-sm font-bold mb-2">
                  {language === "en" ? "Video Length (minutes):" : "Video Süresi (dakika):"}
                </label>
                <input
                  type="number"
                  value={videoLength}
                  onChange={(e) => setVideoLength(parseInt(e.target.value))}
                  min="1"
                  max="60"
                  className="bg-white bg-opacity-20 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400"
                />
              </div>
              
              {script && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-bold text-yellow-400 mb-3">{language === "en" ? "Hook (15-30s):" : "Giriş (15-30s):"}</h3>
                    <div className="bg-white bg-opacity-20 rounded-lg p-4 text-white">
                      {script.hook}
                    </div>
                  </div>
                  
                  {script.sections.map((section, index) => (
                    <div key={index}>
                      <h3 className="text-xl font-bold text-blue-400 mb-3">
                        {language === "en" ? `Section ${index + 1}:` : `Bölüm ${index + 1}:`} {section.title}
                      </h3>
                      <div className="bg-white bg-opacity-20 rounded-lg p-4 text-white">
                        {section.content}
                      </div>
                    </div>
                  ))}
                  
                  <div>
                    <h3 className="text-xl font-bold text-green-400 mb-3">{language === "en" ? "Outro:" : "Sonuç:"}</h3>
                    <div className="bg-white bg-opacity-20 rounded-lg p-4 text-white">
                      {script.outro}
                    </div>
                  </div>
                  
                  <div className="flex gap-4">
                    <button
                      onClick={() => setCurrentStep(3)}
                      className="flex-1 bg-gray-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-gray-700 transition-all duration-300"
                    >
                      {language === "en" ? "Back" : "Geri"}
                    </button>
                    <button
                      onClick={() => {
                        setCurrentStep(5);
                        generateThumbnail();
                      }}
                      className="flex-1 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold py-3 px-6 rounded-lg hover:from-pink-600 hover:to-purple-700 transition-all duration-300"
                    >
                      {language === "en" ? "Next: Thumbnail" : "Sonraki: Thumbnail"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 5: Thumbnail Texts */}
          {currentStep === 5 && (
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-6">
                {language === "en" ? "5. Thumbnail Text Suggestions" : "5. Thumbnail Metin Önerileri"}
              </h2>
              {thumbnailTexts.length > 0 && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {thumbnailTexts.map((text, index) => (
                      <div key={index} className="bg-white bg-opacity-20 rounded-lg p-6 text-center">
                        <div className="text-2xl font-bold text-white mb-2">{text}</div>
                        <div className="text-sm text-gray-300">
                          {language === "en" ? "Thumbnail Text" : "Thumbnail Metni"} {index + 1}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="flex gap-4">
                    <button
                      onClick={() => setCurrentStep(4)}
                      className="flex-1 bg-gray-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-gray-700 transition-all duration-300"
                    >
                      {language === "en" ? "Back" : "Geri"}
                    </button>
                    <button
                      onClick={() => {
                        setCurrentStep(6);
                        analyzeSEO();
                      }}
                      className="flex-1 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold py-3 px-6 rounded-lg hover:from-pink-600 hover:to-purple-700 transition-all duration-300"
                    >
                      {language === "en" ? "Next: SEO Analysis" : "Sonraki: SEO Analizi"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 6: SEO Analysis */}
          {currentStep === 6 && seoScores && (
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-6">
                {language === "en" ? "6. SEO Analysis" : "6. SEO Analizi"}
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {/* SEO Scores */}
                <div className="space-y-4">
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white font-medium">
                        {language === "en" ? "Clickbait Score" : "Dikkat Çekme Skoru"}
                      </span>
                      <span className={`font-bold ${getScoreColor(seoScores.scores.clickbait_score)}`}>
                        {seoScores.scores.clickbait_score}/100
                      </span>
                    </div>
                    <div className="w-full bg-gray-600 rounded-full h-3">
                      <div 
                        className={`h-3 rounded-full ${getScoreBg(seoScores.scores.clickbait_score)}`}
                        style={{width: `${seoScores.scores.clickbait_score}%`}}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white font-medium">
                        {language === "en" ? "Keyword Relevance" : "Anahtar Kelime Uyumu"}
                      </span>
                      <span className={`font-bold ${getScoreColor(seoScores.scores.keyword_relevance_score)}`}>
                        {seoScores.scores.keyword_relevance_score}/100
                      </span>
                    </div>
                    <div className="w-full bg-gray-600 rounded-full h-3">
                      <div 
                        className={`h-3 rounded-full ${getScoreBg(seoScores.scores.keyword_relevance_score)}`}
                        style={{width: `${seoScores.scores.keyword_relevance_score}%`}}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white font-medium">
                        {language === "en" ? "Length Score" : "Uzunluk Skoru"}
                      </span>
                      <span className={`font-bold ${getScoreColor(seoScores.scores.length_score)}`}>
                        {seoScores.scores.length_score}/100
                      </span>
                    </div>
                    <div className="w-full bg-gray-600 rounded-full h-3">
                      <div 
                        className={`h-3 rounded-full ${getScoreBg(seoScores.scores.length_score)}`}
                        style={{width: `${seoScores.scores.length_score}%`}}
                      ></div>
                    </div>
                  </div>
                </div>
                
                {/* Overall Score */}
                <div className="flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-6xl font-bold mb-4 bg-gradient-to-r from-pink-400 to-yellow-400 bg-clip-text text-transparent">
                      {seoScores.scores.overall_seo_score}
                    </div>
                    <div className="text-2xl font-bold text-white mb-2">
                      {language === "en" ? "Overall SEO Score" : "Genel SEO Skoru"}
                    </div>
                    <div className={`text-lg font-medium ${getScoreColor(seoScores.scores.overall_seo_score)}`}>
                      {seoScores.scores.overall_seo_score >= 80 ? (language === "en" ? "Excellent" : "Mükemmel") :
                       seoScores.scores.overall_seo_score >= 60 ? (language === "en" ? "Good" : "İyi") :
                       (language === "en" ? "Needs Improvement" : "Geliştirilmeli")}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Recommendations */}
              {seoScores.recommendations.length > 0 && (
                <div className="bg-white bg-opacity-20 rounded-lg p-6 mb-6">
                  <h3 className="text-xl font-bold text-white mb-4">
                    {language === "en" ? "Recommendations:" : "Öneriler:"}
                  </h3>
                  <ul className="space-y-2 text-white">
                    {seoScores.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-yellow-400 mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="flex gap-4">
                <button
                  onClick={() => setCurrentStep(5)}
                  className="flex-1 bg-gray-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-gray-700 transition-all duration-300"
                >
                  {language === "en" ? "Back" : "Geri"}
                </button>
                <button
                  onClick={resetFlow}
                  className="flex-1 bg-gradient-to-r from-green-500 to-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:from-green-600 hover:to-blue-700 transition-all duration-300"
                >
                  {language === "en" ? "Create New Video" : "Yeni Video Oluştur"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;