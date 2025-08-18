import type { Scenario } from '../types';

export const SAMPLES_PER_SECOND = 50; // Increased for smoother waves
export const DATA_POINTS_COUNT = SAMPLES_PER_SECOND * 8; // Show 8 seconds of data
export const UPDATE_INTERVAL_MS = 1000 / SAMPLES_PER_SECOND;

// Simplified ECG Patterns (P-QRS-T complex)
const NORMAL_SINUS_PATTERN_BASE = [
  0, 0.05, 0.1, // P wave
  0.05, 0, -0.1, // PR segment
  0.5, 1.2, -0.4, 0.2, // QRS complex
  0, 0.1, 0.2, 0.3, 0.25, // T wave
  0.15, 0 // End of T wave
];

// Plethysmograph pattern base (normalized 0 to 1)
const PLETH_NORMAL_PATTERN_BASE = [
  0.1, 0.2, 0.5, 0.9, 1.0, // Anacrotic limb to peak
  0.8, 0.65, 0.7, // Dicrotic notch
  0.5, 0.3, 0.15, 0.1 // Dicrotic limb to baseline
];

// Respiration pattern base (sine-like, normalized -0.5 to 0.5)
const RESP_NORMAL_PATTERN_BASE = [
  0, 0.15, 0.3, 0.4, 0.5, // Inspiration
  0.4, 0.3, 0.15, 0, // Expiration start
  -0.15, -0.3, -0.4, -0.5, // Expiration deeper
  -0.4, -0.3, -0.15, 0 // Return to baseline
];


const createPattern = (base: number[], targetLengthFraction: number = 0.5): number[] => {
  // targetLengthFraction is fraction of SAMPLES_PER_SECOND, e.g. 0.5 for a pattern that's 0.5s long
  const targetLength = Math.max(5, Math.floor(SAMPLES_PER_SECOND * targetLengthFraction));
  if (base.length === 0) return Array(targetLength).fill(0);
  if (base.length === 1 && base[0] === 0) return Array(targetLength).fill(0); // Asystole/Apnea
  if (base.length === 1) return Array(targetLength).fill(base[0]);
  
  const result: number[] = [];
  for (let i = 0; i < targetLength; i++) {
    const baseIndex = (i / (targetLength -1 )) * (base.length - 1); // Ensure last point of base is hit
    const idx1 = Math.floor(baseIndex);
    const idx2 = Math.min(idx1 + 1, base.length - 1);
    const frac = baseIndex - idx1;
    result.push(base[idx1] * (1 - frac) + base[idx2] * frac);
  }
  return result;
};

export const NORMAL_SINUS_PATTERN = createPattern(NORMAL_SINUS_PATTERN_BASE, 0.7); // Approx 0.7s for a beat at ~85bpm base, rate adjusts
export const TACHYCARDIA_PATTERN = createPattern(NORMAL_SINUS_PATTERN_BASE, 0.4); 
export const BRADYCARDIA_PATTERN = createPattern(NORMAL_SINUS_PATTERN_BASE, 1.0); 
export const ASYSTOLE_PATTERN = createPattern([0], 1.0); // Flat line
export const VF_PATTERN = createPattern([0, 0.1, -0.1, 0.2, -0.2], 0.2); // Base for VF, mostly overridden

export const PLETH_NORMAL_PATTERN = createPattern(PLETH_NORMAL_PATTERN_BASE, 0.7);
export const PLETH_LOW_PERFUSION_PATTERN = createPattern(PLETH_NORMAL_PATTERN_BASE.map(p => p * 0.5), 0.7); // Smaller amplitude
export const PLETH_FLAT_PATTERN = createPattern([0], 1.0);

export const RESP_NORMAL_PATTERN = createPattern(RESP_NORMAL_PATTERN_BASE, 3.0); // ~3-4s per breath cycle
export const RESP_TACHYPNEA_PATTERN = createPattern(RESP_NORMAL_PATTERN_BASE, 1.5);
export const RESP_BRADYPNEA_PATTERN = createPattern(RESP_NORMAL_PATTERN_BASE, 5.0);
export const RESP_APNEA_PATTERN = createPattern([0], 1.0);


export const SCENARIOS: Scenario[] = [
  {
    id: 'normal_sinus',
    name: 'Rythme Sinusal Normal',
    bpm: 75,
    basePattern: NORMAL_SINUS_PATTERN,
    lineColor: 'stroke-green-400',
    textColor: 'text-green-400',
    spo2: 98,
    plethBasePattern: PLETH_NORMAL_PATTERN,
    plethLineColor: 'stroke-cyan-400',
    plethTextColor: 'text-cyan-400',
    respRate: 16,
    respBasePattern: RESP_NORMAL_PATTERN,
    respLineColor: 'stroke-yellow-300',
    respTextColor: 'text-yellow-300',
    nibp: { systolic: 120, diastolic: 80 },
  },
  {
    id: 'tachycardia',
    name: 'Tachycardie',
    bpm: 130,
    basePattern: TACHYCARDIA_PATTERN,
    lineColor: 'stroke-yellow-400',
    textColor: 'text-yellow-400',
    spo2: 97,
    plethBasePattern: PLETH_NORMAL_PATTERN,
    plethLineColor: 'stroke-cyan-400',
    plethTextColor: 'text-cyan-400',
    respRate: 22,
    respBasePattern: RESP_TACHYPNEA_PATTERN,
    respLineColor: 'stroke-yellow-300',
    respTextColor: 'text-yellow-300',
    nibp: { systolic: 130, diastolic: 85 },
  },
  {
    id: 'bradycardia',
    name: 'Bradycardie',
    bpm: 45,
    basePattern: BRADYCARDIA_PATTERN,
    lineColor: 'stroke-blue-400',
    textColor: 'text-blue-400',
    spo2: 99,
    plethBasePattern: PLETH_NORMAL_PATTERN,
    plethLineColor: 'stroke-cyan-400',
    plethTextColor: 'text-cyan-400',
    respRate: 10,
    respBasePattern: RESP_BRADYPNEA_PATTERN,
    respLineColor: 'stroke-yellow-300',
    respTextColor: 'text-yellow-300',
    nibp: { systolic: 100, diastolic: 60 },
  },
  {
    id: 'asystole',
    name: 'Asystolie',
    bpm: 0,
    basePattern: ASYSTOLE_PATTERN,
    lineColor: 'stroke-red-500',
    textColor: 'text-red-500',
    spo2: 0,
    plethBasePattern: PLETH_FLAT_PATTERN,
    plethLineColor: 'stroke-red-500',
    plethTextColor: 'text-red-500',
    respRate: 0,
    respBasePattern: RESP_APNEA_PATTERN,
    respLineColor: 'stroke-red-500',
    respTextColor: 'text-red-500',
    nibp: { systolic: 0, diastolic: 0 },
  },
  {
    id: 'vf',
    name: 'Fibrillation Ventriculaire',
    bpm: 0, // Effective BPM is unmeasurable, scope shows "---"
    basePattern: VF_PATTERN, 
    lineColor: 'stroke-purple-500',
    textColor: 'text-purple-500',
    spo2: 60, // Rapidly declining
    plethBasePattern: PLETH_LOW_PERFUSION_PATTERN, // Or becoming flat/erratic
    plethLineColor: 'stroke-purple-400',
    plethTextColor: 'text-purple-400',
    respRate: 0, // Agonal or absent, effectively 0 for consistent display
    respBasePattern: RESP_APNEA_PATTERN, // Can be agonal, but model as apnea
    respLineColor: 'stroke-purple-400',
    respTextColor: 'text-purple-400',
    nibp: { systolic: 0, diastolic: 0 }, 
  },
];

export const DEFAULT_SCENARIO_INDEX = 0;
