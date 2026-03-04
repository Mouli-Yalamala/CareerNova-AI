import { useState, useRef } from 'react'
import { Upload, Search, Rocket, Zap, BookOpen, ChevronRight, AlertCircle, CheckCircle2, Loader2, ExternalLink, FileText, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  const [resumeFile, setResumeFile] = useState(null)
  const [resumeText, setResumeText] = useState('')
  const [useTextMode, setUseTextMode] = useState(false)
  const [jobQuery, setJobQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setResumeFile(file)
      setError(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Validation
    if (!jobQuery) {
      setError("Please enter a target job role.")
      return
    }

    if (!useTextMode && !resumeFile) {
      setError("Please upload your resume file.")
      return
    }

    if (useTextMode && !resumeText.trim()) {
      setError("Please paste your resume content.")
      return
    }

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('job_query', jobQuery)

    if (useTextMode) {
      const blob = new Blob([resumeText], { type: 'text/plain' })
      const file = new File([blob], 'resume.txt', { type: 'text/plain' })
      formData.append('resume', file)
    } else {
      formData.append('resume', resumeFile)
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/run_pipeline`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (response.data.success === false && response.data.error_message) {
        setError(response.data.error_message)
        setResult(null)
      } else {
        setResult(response.data)
      }
    } catch (err) {
      console.error("Pipeline error:", err)
      const detail = err.response?.data?.detail
      setError(Array.isArray(detail) ? detail[0]?.msg : detail || "The pipeline encountered an error. Please check your backend and credits.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen text-slate-200 p-6 md:p-12 font-sans selection:bg-indigo-500/30 overflow-x-hidden">
      {/* Background Decorative Elements */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-emerald-500/10 blur-[120px] rounded-full" />
      </div>

      <main className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-16">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => { setResult(null); setError(null); }}>
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Rocket className="text-white w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white italic">Career<span className="text-indigo-500 not-italic">Nova</span></h1>
          </div>
          <nav className="hidden md:flex gap-8 text-sm font-medium text-slate-400">
            <button onClick={() => { setResult(null); setError(null); }} className="hover:text-white transition-colors">Analyzer</button>
            <a href="#" className="hover:text-white transition-colors">History</a>
          </nav>
        </header>

        <AnimatePresence mode="wait">
          {!result ? (
            <motion.div
              key="landing"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="grid lg:grid-cols-2 gap-12 items-center"
            >
              <div>
                <h2 className="text-5xl md:text-6xl font-extrabold text-white leading-tight mb-6">
                  Ignite Your <br />
                  <span className="gradient-text">Potential.</span>
                </h2>
                <p className="text-slate-400 text-lg mb-8 max-w-md leading-relaxed">
                  CareerNova uses high-IQ agents to bridge the gap between your profile and your dream role.
                </p>

                <div className="flex flex-wrap gap-4">
                  <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-effect text-xs font-medium border-slate-700">
                    <Zap className="w-3 h-3 text-emerald-400" /> AI Orchestration
                  </div>
                  <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-effect text-xs font-medium border-slate-700">
                    <BookOpen className="w-3 h-3 text-indigo-400" /> Interactive Roadmaps
                  </div>
                </div>
              </div>

              <div className="glass-effect p-8 rounded-3xl shadow-2xl relative overflow-hidden group border border-white/5 flex flex-col gap-6">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-emerald-500 opacity-50" />

                {error && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-red-500/10 border border-red-500/40 text-red-200 p-4 rounded-xl flex items-start gap-3 text-sm break-words relative overflow-hidden"
                  >
                    <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0 pr-6">
                      <p className="font-medium whitespace-pre-wrap leading-tight">{error}</p>
                    </div>
                    <button onClick={() => setError(null)} className="absolute right-3 top-3 hover:text-white">
                      <X className="w-4 h-4" />
                    </button>
                  </motion.div>
                )}

                <div className="space-y-6">
                  {/* Job Query Input */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Target Career Path</label>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                      <input
                        type="text"
                        placeholder="e.g. Lead Product Manager"
                        className="w-full bg-slate-900/50 border border-slate-700 rounded-xl py-3 pl-11 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all placeholder:text-slate-600 font-medium"
                        value={jobQuery}
                        onChange={(e) => setJobQuery(e.target.value)}
                        disabled={loading}
                      />
                    </div>
                  </div>

                  {/* Resume Upload Section */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="block text-sm font-medium text-slate-300">Your Expertise</label>
                      <button
                        onClick={() => { setUseTextMode(!useTextMode); setError(null); }}
                        className="text-xs text-indigo-400 hover:text-indigo-300 font-bold"
                      >
                        {useTextMode ? "Upload File" : "Paste Content"}
                      </button>
                    </div>

                    {!useTextMode ? (
                      <div
                        onClick={() => fileInputRef.current?.click()}
                        className={`w-full border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${resumeFile ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-slate-700 hover:border-indigo-500/50 hover:bg-slate-800/20'}`}
                      >
                        <input
                          type="file"
                          ref={fileInputRef}
                          className="hidden"
                          onChange={handleFileChange}
                          accept=".pdf,.docx,.txt"
                        />
                        {resumeFile ? (
                          <div className="flex items-center gap-3 w-full justify-center">
                            <FileText className="w-8 h-8 text-emerald-400 shrink-0" />
                            <div className="text-left overflow-hidden">
                              <p className="text-white font-bold text-sm truncate">{resumeFile.name}</p>
                              <p className="text-slate-500 text-xs">{(resumeFile.size / 1024).toFixed(1)} KB</p>
                            </div>
                            <button
                              onClick={(e) => { e.stopPropagation(); setResumeFile(null); }}
                              className="p-1.5 bg-slate-800/50 hover:bg-slate-700 rounded-lg"
                            >
                              <X className="w-4 h-4 text-slate-400" />
                            </button>
                          </div>
                        ) : (
                          <>
                            <Upload className="w-10 h-10 text-slate-500 mb-2" />
                            <p className="text-sm text-slate-400 font-medium text-center px-4">Click to select PDF, DOCX, or TXT</p>
                          </>
                        )}
                      </div>
                    ) : (
                      <div className="relative">
                        <Upload className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                        <textarea
                          placeholder="Paste your professional experience here..."
                          className="w-full bg-slate-900/50 border border-slate-700 rounded-xl py-3 pl-11 pr-4 h-32 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all placeholder:text-slate-600 resize-none font-medium leading-relaxed"
                          value={resumeText}
                          onChange={(e) => setResumeText(e.target.value)}
                          disabled={loading}
                        />
                      </div>
                    )}
                  </div>

                  <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700/50 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 group transition-all shadow-lg shadow-indigo-600/20 active:scale-95"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Synchronizing Agents...
                      </>
                    ) : (
                      <>
                        Launch CareerNova
                        <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                      </>
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-8 pb-20"
            >
              {/* Result Summary Bar */}
              <div className="flex flex-col md:flex-row gap-6 items-start md:items-center justify-between p-8 glass-effect rounded-3xl border border-white/5">
                <div className="flex gap-6 items-center">
                  <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
                    <svg className="w-full h-full -rotate-90">
                      <circle cx="48" cy="48" r="40" fill="transparent" stroke="currentColor" strokeWidth="8" className="text-slate-800" />
                      <circle cx="48" cy="48" r="40" fill="transparent" stroke="currentColor" strokeWidth="8" strokeDasharray={251.2} strokeDashoffset={251.2 * (1 - result.skill_gap_analysis.match_score / 100)} className="text-indigo-500 transition-all duration-1000 ease-out" />
                    </svg>
                    <span className="absolute text-xl font-bold text-white">{Math.round(result.skill_gap_analysis.match_score)}%</span>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">Match Accuracy</h3>
                    <p className="text-slate-400 leading-tight">{result.skill_gap_analysis.recommendation}</p>
                  </div>
                </div>

                <div className="flex gap-3 shrink-0">
                  <div className="px-6 py-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 text-center">
                    <span className="block text-xs uppercase tracking-wider text-indigo-400 font-bold mb-1">Status</span>
                    <span className="text-white font-medium">Verified</span>
                  </div>
                  <div className="px-6 py-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 text-center">
                    <span className="block text-xs uppercase tracking-wider text-emerald-400 font-bold mb-1">Time</span>
                    <span className="text-white font-medium">{result.execution_time}s</span>
                  </div>
                </div>
              </div>

              {/* Main Content Sections */}
              <div className="grid md:grid-cols-2 gap-8">
                {/* Roadmap Section */}
                <section className="glass-effect p-8 rounded-3xl border border-white/5">
                  <div className="flex items-center gap-3 mb-8">
                    <div className="p-2 bg-emerald-500/20 rounded-lg">
                      <BookOpen className="w-6 h-6 text-emerald-400" />
                    </div>
                    <h3 className="text-xl font-bold text-white">Learning Roadmap</h3>
                  </div>

                  <div className="space-y-4">
                    {result.skill_gap_analysis.roadmap.map((step, i) => (
                      <div key={i} className="p-5 bg-slate-900/50 rounded-2xl border border-slate-700/50 group hover:border-indigo-500/30 transition-colors">
                        <div className="flex justify-between items-start mb-3">
                          <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Step {step.step}</span>
                          <span className={`text-[10px] font-bold px-2 py-1 rounded-md uppercase ${step.priority === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'}`}>
                            {step.priority} Priority
                          </span>
                        </div>
                        <h4 className="text-white font-bold text-lg mb-4">{step.skill}</h4>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(step.resources).map(([type, links], j) => (
                            Array.isArray(links) ? links.map((link, k) => (
                              <a key={`${j}-${k}`} href={link} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-medium transition-colors">
                                {type.charAt(0).toUpperCase() + type.slice(1)} <ExternalLink className="w-3 h-3" />
                              </a>
                            )) : (
                              <a key={j} href={links} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-xs font-medium transition-colors">
                                {type.charAt(0).toUpperCase() + type.slice(1)} <ExternalLink className="w-3 h-3" />
                              </a>
                            )
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Applications Section */}
                <section className="glass-effect p-8 rounded-3xl border border-white/5">
                  <div className="flex items-center gap-3 mb-8">
                    <div className="p-2 bg-indigo-500/20 rounded-lg">
                      <CheckCircle2 className="w-6 h-6 text-indigo-400" />
                    </div>
                    <h3 className="text-xl font-bold text-white">Application Materials</h3>
                  </div>

                  {result.skill_gap_analysis.match_score < 50 ? (
                    <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-6 text-center">
                      <AlertCircle className="w-8 h-8 text-amber-500 mx-auto mb-3 shrink-0" />
                      <h4 className="text-white font-bold mb-2">Generation Skipped</h4>
                      <p className="text-slate-400 text-sm">Your match score is below 50%. Focus on the roadmap skills to increase your chances.</p>
                    </div>
                  ) : (
                    <div className="space-y-6">


                      {/* Cover Letter */}
                      <div className="p-6 bg-slate-900/50 rounded-2xl border border-slate-700/50">
                        <div className="flex justify-between items-center mb-4">
                          <h4 className="text-white font-bold flex items-center gap-2">
                            Tailored Cover Letter
                          </h4>
                          <button
                            onClick={() => navigator.clipboard.writeText(result.application_materials.cover_letter)}
                            className="text-xs text-indigo-400 hover:text-indigo-300 font-bold"
                          >
                            Copy Text
                          </button>
                        </div>
                        <p className="text-slate-400 text-sm line-clamp-6 leading-relaxed italic break-words whitespace-pre-wrap">
                          "{result.application_materials.cover_letter}"
                        </p>
                      </div>

                      {/* Recruiter Email */}
                      <div className="p-6 bg-slate-900/50 rounded-2xl border border-slate-700/50">
                        <div className="flex justify-between items-center mb-4">
                          <h4 className="text-white font-bold flex items-center gap-2">
                            Recruiter Email
                          </h4>
                          <button
                            onClick={() => navigator.clipboard.writeText(result.application_materials.recruiter_email)}
                            className="text-xs text-indigo-400 hover:text-indigo-300 font-bold"
                          >
                            Copy Text
                          </button>
                        </div>
                        <p className="text-slate-400 text-sm line-clamp-6 leading-relaxed whitespace-pre-wrap break-words">
                          {result.application_materials.recruiter_email}
                        </p>
                      </div>

                      {/* LinkedIn Message */}
                      <div className="p-6 bg-slate-900/50 rounded-2xl border border-slate-700/50">
                        <div className="flex justify-between items-center mb-4">
                          <h4 className="text-white font-bold flex items-center gap-2">
                            LinkedIn Message
                          </h4>
                          <button
                            onClick={() => navigator.clipboard.writeText(result.application_materials.linkedin_message)}
                            className="text-xs text-indigo-400 hover:text-indigo-300 font-bold"
                          >
                            Copy Text
                          </button>
                        </div>
                        <p className="text-slate-400 text-sm line-clamp-3 leading-relaxed break-words whitespace-pre-wrap">
                          {result.application_materials.linkedin_message}
                        </p>
                      </div>
                    </div>
                  )}
                </section>
              </div>

              {/* Jobs Grid */}
              <section>
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <Search className="w-5 h-5 text-slate-500" />
                  Top Matched Jobs
                </h3>
                <div className="grid md:grid-cols-3 gap-6">
                  {result.job_scrapings.map((job, i) => (
                    <a key={i} href={job.url} target="_blank" rel="noreferrer" className="group p-6 glass-effect rounded-2xl border border-white/5 hover:border-indigo-500/50 transition-all hover:-translate-y-1 overflow-hidden">
                      <div className="flex justify-between items-start mb-4">
                        <div className="w-10 h-10 bg-slate-800 rounded-lg flex items-center justify-center text-xs font-bold text-slate-400">
                          {job.company_name[0]}
                        </div>
                        <ExternalLink className="w-4 h-4 text-slate-600 group-hover:text-indigo-400 transition-colors" />
                      </div>
                      <h4 className="text-white font-bold mb-1 group-hover:text-indigo-400 transition-colors truncate">{job.job_title}</h4>
                      <p className="text-slate-500 text-xs font-medium mb-4 truncate">{job.company_name} • {job.location}</p>
                      <div className="flex flex-wrap gap-1.5 line-clamp-1">
                        {job.skills_required.slice(0, 3).map((skill, j) => (
                          <span key={j} className="text-[10px] px-2 py-0.5 bg-slate-800 text-slate-400 rounded-md">{skill}</span>
                        ))}
                      </div>
                    </a>
                  ))}
                </div>
              </section>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App
