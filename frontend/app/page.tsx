"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { Activity, Cpu, Brain, ArrowUpRight } from "lucide-react";

// Deterministic waveform — peak region at bars 28–45
const BARS = Array.from({ length: 80 }, (_, i) => {
  const base =
    Math.sin(i * 0.15) * 20 +
    Math.sin(i * 0.31) * 14 +
    Math.sin(i * 0.07) * 9 +
    44;
  const peak =
    i >= 28 && i <= 45
      ? Math.sin(((i - 28) * Math.PI) / 17) * 46
      : 0;
  return Math.max(8, Math.min(98, Math.round(base + peak)));
});

const fadeUp = {
  hidden: { opacity: 0, y: 22 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.65, ease: [0.25, 0.1, 0.25, 1] as const },
  },
};

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.11 } },
};

const STATS = [
  { label: "PEAK TIMESTAMP", value: "2:23", sub: "of 3:47" },
  { label: "SOCIAL VELOCITY", value: "94.2", sub: "confidence" },
  { label: "SKIP PROBABILITY", value: "2.1%", sub: "within window" },
  { label: "PREDICTED LOOPS", value: "3.8×", sub: "avg listener" },
];

const STEPS = [
  {
    number: "01",
    icon: <Activity size={18} />,
    title: "Signal Processing",
    description:
      "Raw audio is decomposed into spectral features, MFCCs, and temporal dynamics at 44.1 kHz resolution. Each track is segmented into 100 ms frames for granular analysis.",
    details: ["FFT decomposition", "Mel-spectrogram encoding", "Temporal windowing"],
    tag: null,
  },
  {
    number: "02",
    icon: <Cpu size={18} />,
    title: "Neural Inference",
    description:
      "A distilled transformer trained on 2.4 M tracks processes the encoded signal. TRIBE v2 maps acoustic patterns to human attentional response probabilities.",
    details: ["340 M parameter model", "2.4 M training tracks", "12 ms inference latency"],
    tag: "TRIBE v2",
  },
  {
    number: "03",
    icon: <Brain size={18} />,
    title: "Attention Mapping",
    description:
      "Output logits decode into a continuous attention curve. The Viral 15 algorithm isolates the peak 15-second window, scored for social-platform hook performance.",
    details: ["Attention curve generation", "Peak window isolation", "Skip probability scoring"],
    tag: null,
  },
];

export default function Home() {
  return (
    <div
      className="min-h-screen text-white relative"
      style={{ background: "var(--background)", fontFamily: "var(--font-geist-sans)" }}
    >
      {/* Dot-grid background */}
      <div
        aria-hidden
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          backgroundImage:
            "radial-gradient(circle, #1a1a3a 1px, transparent 1px)",
          backgroundSize: "30px 30px",
        }}
      />

      {/* ── NAV ── */}
      <nav
        className="relative z-10 border-b px-6 py-4"
        style={{ borderColor: "var(--border-dim)" }}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src="/sillage-wake-color-dark-512px.png"
              alt="Sillage logo"
              width={26}
              height={26}
            />
            <span
              className="text-[11px] font-bold tracking-[0.18em] text-white"
              style={{ fontFamily: "var(--font-geist-mono)" }}
            >
              SILLAGE
            </span>
          </div>

          <button
            className="text-[11px] tracking-widest border px-4 py-2 transition-all"
            style={{
              fontFamily: "var(--font-geist-mono)",
              borderColor: "#333",
              color: "#888",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "#ffffff";
              e.currentTarget.style.color = "#ffffff";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "#333";
              e.currentTarget.style.color = "#888";
            }}
          >
            REQUEST ACCESS →
          </button>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section
        className="relative z-10 border-b overflow-hidden"
        style={{ borderColor: "var(--border-dim)" }}
      >
        {/* Large background logo */}
        <div
          aria-hidden
          className="absolute right-[-60px] top-1/2 -translate-y-1/2 pointer-events-none hidden lg:block"
          style={{ opacity: 0.04 }}
        >
          <Image
            src="/sillage-arc-color-dark-512px.png"
            alt=""
            width={700}
            height={700}
          />
        </div>

        <div className="max-w-7xl mx-auto px-6 py-28 md:py-44">
          <motion.div
            variants={stagger}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="max-w-4xl"
          >
            <motion.span
              variants={fadeUp}
              className="text-[10px] tracking-[0.35em] mb-8 block"
              style={{
                fontFamily: "var(--font-geist-mono)",
                color: "var(--text-muted)",
              }}
            >
              SILLAGE / BIOLOGICAL AUDIO ANALYSIS
            </motion.span>

            <motion.h1
              variants={fadeUp}
              className="text-5xl md:text-7xl lg:text-[88px] font-bold tracking-tight text-white leading-[0.95] mb-8"
            >
              Biological
              <br />
              Audio
              <br />
              Analysis.
            </motion.h1>

            <motion.p
              variants={fadeUp}
              className="text-sm leading-relaxed max-w-lg mb-12"
              style={{
                fontFamily: "var(--font-geist-mono)",
                color: "var(--text-muted)",
              }}
            >
              Predict human attention intervals using distilled neural foundation
              models. Built for producers, artists, and labels.
            </motion.p>

            <motion.div
              variants={fadeUp}
              className="flex flex-col sm:flex-row gap-4"
            >
              <a href="mailto:ryousuf569@gmail.com" className="inline-block">
                <button
                  className="flex items-center justify-center gap-2 bg-white text-[#050505] text-sm font-semibold px-8 py-4 transition-colors tracking-wide"
                  onMouseEnter={(e) => (e.currentTarget.style.background = "#d4d4d4")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "#ffffff")}
                >
                  Stay Tuned
                  <ArrowUpRight size={15} />
                </button>
              </a>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ── VIRAL 15 CARD ── */}
      <section
        className="relative z-10 border-b"
        style={{ borderColor: "var(--border-dim)" }}
      >
        <div className="max-w-7xl mx-auto px-6 py-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.15 }}
            transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
          >
            {/* Section header */}
            <div
              className="flex flex-col md:flex-row md:items-end justify-between mb-8 pb-6 border-b gap-4"
              style={{ borderColor: "var(--border-dim)" }}
            >
              <div>
                <span
                  className="text-[10px] tracking-[0.32em] block mb-2"
                  style={{
                    fontFamily: "var(--font-geist-mono)",
                    color: "var(--text-muted)",
                  }}
                >
                  UTILITY / ROLLING WINDOW CALCULATION
                </span>
                <h2 className="text-2xl md:text-3xl font-bold text-white">
                  Social Engagement Peak Detection
                </h2>
              </div>
              <div
                className="flex items-center gap-2 border self-start md:self-auto px-3 py-1.5"
                style={{ borderColor: "#333" }}
              >
                <div
                  className="w-1.5 h-1.5 rounded-full pulse-dot"
                  style={{ background: "var(--accent-purple)" }}
                />
                <span
                  className="text-[10px] tracking-widest"
                  style={{
                    fontFamily: "var(--font-geist-mono)",
                    color: "var(--accent-purple)",
                  }}
                >
                  VIRAL 15
                </span>
              </div>
            </div>

            {/* Card */}
            <div
              className="border"
              style={{ background: "#0d0d26", borderColor: "var(--border-dim)" }}
            >
              {/* Card header row */}
              <div
                className="border-b px-6 py-3 flex flex-wrap items-center justify-between gap-3"
                style={{ borderColor: "var(--border-dim)" }}
              >
                <div className="flex items-center gap-3">
                  <Activity size={13} style={{ color: "var(--text-dim)" }} />
                  <span
                    className="text-[10px]"
                    style={{
                      fontFamily: "var(--font-geist-mono)",
                      color: "var(--text-dim)",
                    }}
                  >
                    AMPLITUDE / SOCIAL VELOCITY — TRACK_ID: 8a3f2c91
                  </span>
                </div>
                <div className="flex items-center gap-6">
                  {[
                    ["BPM", "124"],
                    ["KEY", "A♭m"],
                    ["LEN", "3:47"],
                  ].map(([k, v]) => (
                    <span
                      key={k}
                      className="text-[10px]"
                      style={{
                        fontFamily: "var(--font-geist-mono)",
                        color: "#3a3a3a",
                      }}
                    >
                      {k}: {v}
                    </span>
                  ))}
                </div>
              </div>

              {/* Waveform */}
              <div className="px-6 pt-8 pb-4 relative">
                {/* Timestamp labels */}
                <div className="flex justify-between mb-3">
                  {["0:00", "0:57", "1:53", "2:50", "3:47"].map((t) => (
                    <span
                      key={t}
                      className="text-[9px]"
                      style={{
                        fontFamily: "var(--font-geist-mono)",
                        color: "#3a3a3a",
                      }}
                    >
                      {t}
                    </span>
                  ))}
                </div>

                {/* Bars */}
                <div className="relative h-28 flex items-end gap-[1.5px]">
                  {BARS.map((h, i) => {
                    const isPeak = i >= 28 && i <= 45;
                    return (
                      <motion.div
                        key={i}
                        className="flex-1 origin-bottom rounded-[1px]"
                        style={{
                          height: `${h}%`,
                          background: isPeak
                            ? "linear-gradient(to top, #7c6fcd, #5b9bd5)"
                            : "#181836",
                        }}
                        initial={{ scaleY: 0 }}
                        whileInView={{ scaleY: 1 }}
                        viewport={{ once: true }}
                        transition={{
                          duration: 0.35,
                          delay: i * 0.007,
                          ease: "easeOut",
                        }}
                      />
                    );
                  })}

                  {/* Peak window bracket */}
                  <div
                    className="absolute top-0 bottom-0 border-l border-r border-t pointer-events-none"
                    style={{
                      left: `${(28 / 80) * 100}%`,
                      width: `${(18 / 80) * 100}%`,
                      borderColor: "rgba(124,111,205,0.25)",
                    }}
                  >
                    <span
                      className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-[9px] tracking-widest"
                      style={{
                        fontFamily: "var(--font-geist-mono)",
                        color: "var(--accent-purple)",
                      }}
                    >
                      VIRAL 15 · 2:23–2:38
                    </span>
                  </div>
                </div>
              </div>

              {/* Stats grid */}
              <div
                className="border-t grid grid-cols-2 md:grid-cols-4"
                style={{ borderColor: "var(--border-dim)" }}
              >
                {STATS.map((s, i) => (
                  <div
                    key={i}
                    className="px-6 py-5"
                    style={{
                      borderRight:
                        i < 3 ? "1px solid var(--border-dim)" : undefined,
                      borderTop:
                        i >= 2 ? "1px solid var(--border-dim)" : undefined,
                    }}
                  >
                    <span
                      className="text-[9px] tracking-widest block mb-2"
                      style={{
                        fontFamily: "var(--font-geist-mono)",
                        color: "#3a3a3a",
                      }}
                    >
                      {s.label}
                    </span>
                    <span className="text-2xl font-bold text-white block">
                      {s.value}
                    </span>
                    <span
                      className="text-[10px] mt-1 block"
                      style={{
                        fontFamily: "var(--font-geist-mono)",
                        color: "#444",
                      }}
                    >
                      {s.sub}
                    </span>
                  </div>
                ))}
              </div>

              {/* Analysis progress bar */}
              <div
                className="border-t px-6 py-3 flex items-center gap-4"
                style={{ borderColor: "var(--border-dim)" }}
              >
                <span
                  className="text-[9px] tracking-widest shrink-0"
                  style={{
                    fontFamily: "var(--font-geist-mono)",
                    color: "#3a3a3a",
                  }}
                >
                  ANALYSIS COMPLETE
                </span>
                <div
                  className="flex-1 h-px relative overflow-hidden"
                  style={{ background: "#14143a" }}
                >
                  <motion.div
                    className="absolute inset-y-0 left-0"
                    style={{
                      background:
                        "linear-gradient(to right, #7c6fcd, #5b9bd5)",
                    }}
                    initial={{ width: 0 }}
                    whileInView={{ width: "87%" }}
                    viewport={{ once: true }}
                    transition={{ duration: 2.6, delay: 0.6, ease: "linear" }}
                  />
                </div>
                <span
                  className="text-[9px] shrink-0"
                  style={{
                    fontFamily: "var(--font-geist-mono)",
                    color: "var(--accent-purple)",
                  }}
                >
                  87%
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── PROCESS ── */}
      <section
        className="relative z-10 border-b"
        style={{ borderColor: "var(--border-dim)" }}
      >
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="mb-14">
            <span
              className="text-[10px] tracking-[0.32em] block mb-4"
              style={{
                fontFamily: "var(--font-geist-mono)",
                color: "var(--text-muted)",
              }}
            >
              METHODOLOGY / INFERENCE PIPELINE
            </span>
            <h2 className="text-2xl md:text-3xl font-bold text-white">
              How It Works
            </h2>
          </div>

          <motion.div
            variants={stagger}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, amount: 0.15 }}
            className="grid grid-cols-1 md:grid-cols-3"
          >
            {STEPS.map((step, i) => (
              <motion.div
                key={i}
                variants={fadeUp}
                className="pt-8 pb-8"
                style={{
                  borderTop: "1px solid var(--border-dim)",
                  borderRight:
                    i < 2 ? "1px solid var(--border-dim)" : undefined,
                  paddingRight: i < 2 ? "2rem" : undefined,
                  paddingLeft: i > 0 ? "2rem" : undefined,
                }}
              >
                {/* Number + tag + icon */}
                <div className="flex items-start justify-between mb-6">
                  <span
                    className="text-5xl font-bold leading-none"
                    style={{
                      fontFamily: "var(--font-geist-mono)",
                      color: "#1c1c40",
                    }}
                  >
                    {step.number}
                  </span>
                  <div className="flex items-center gap-2">
                    {step.tag && (
                      <span
                        className="text-[9px] tracking-widest border px-2 py-1"
                        style={{
                          fontFamily: "var(--font-geist-mono)",
                          borderColor: "#2a2a2a",
                          color: "#555",
                        }}
                      >
                        {step.tag}
                      </span>
                    )}
                    <span style={{ color: "#333" }}>{step.icon}</span>
                  </div>
                </div>

                <h3 className="text-base font-semibold text-white mb-3">
                  {step.title}
                </h3>
                <p
                  className="text-[11px] leading-relaxed mb-6"
                  style={{
                    fontFamily: "var(--font-geist-mono)",
                    color: "#555",
                  }}
                >
                  {step.description}
                </p>

                <ul className="space-y-2">
                  {step.details.map((d) => (
                    <li
                      key={d}
                      className="flex items-center gap-2 text-[10px]"
                      style={{
                        fontFamily: "var(--font-geist-mono)",
                        color: "#3a3a3a",
                      }}
                    >
                      <div
                        className="w-1 h-1 rounded-full shrink-0"
                        style={{ background: "#2e2e2e" }}
                      />
                      {d}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="relative z-10">
        <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Image
              src="/sillage-arc-color-dark-512px.png"
              alt="Sillage"
              width={18}
              height={18}
            />
            <span
              className="text-[10px] tracking-[0.2em]"
              style={{
                fontFamily: "var(--font-geist-mono)",
                color: "#3a3a3a",
              }}
            >
              SILLAGE © 2026
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}