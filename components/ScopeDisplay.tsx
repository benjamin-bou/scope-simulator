import React from 'react';
import { WaveformTrace } from './ECGTrace'; // Still named ECGTrace here, but it's the new WaveformTrace
import { VitalsDisplay } from './VitalsDisplay';
import type { Scenario } from '../types';
import { ASYSTOLE_PATTERN, PLETH_FLAT_PATTERN, RESP_APNEA_PATTERN } from '../constants'; // For fallback patterns

interface ScopeDisplayProps {
  scenario: Scenario;
}

export const ScopeDisplay: React.FC<ScopeDisplayProps> = ({ scenario }) => {
  return (
    <div className="w-full max-w-6xl h-[700px] sm:h-[600px] bg-black rounded-lg shadow-2xl p-2 border-2 border-slate-700 grid grid-cols-[minmax(0,_3fr)_minmax(0,_1fr)] gap-2">
      {/* Left Column: Traces */}
      <div className="grid grid-rows-3 gap-1 h-full overflow-hidden">
        <div className="bg-slate-800 rounded p-1 overflow-hidden min-h-0">
          <WaveformTrace
            basePattern={scenario.basePattern}
            lineColor={scenario.lineColor}
            targetRate={scenario.bpm}
            valueType="ecg"
            scenarioId={scenario.id}
            yDomain={[-1.5, 2]} // Typical ECG Y-domain
          />
        </div>
        <div className="bg-slate-800 rounded p-1 overflow-hidden min-h-0">
          <WaveformTrace
            basePattern={scenario.plethBasePattern || PLETH_FLAT_PATTERN}
            lineColor={scenario.plethLineColor || 'stroke-gray-500'}
            targetRate={scenario.bpm} // Pleth rate often tied to BPM
            valueType="pleth"
            scenarioId={scenario.id}
            yDomain={[-0.2, 1.2]} // Typical Pleth Y-domain (0-1, with some margin)
          />
        </div>
        <div className="bg-slate-800 rounded p-1 overflow-hidden min-h-0">
          <WaveformTrace
            basePattern={scenario.respBasePattern || RESP_APNEA_PATTERN}
            lineColor={scenario.respLineColor || 'stroke-gray-500'}
            targetRate={scenario.respRate !== undefined ? scenario.respRate : 0}
            valueType="resp"
            scenarioId={scenario.id}
            yDomain={[-0.6, 0.6]} // Typical Respiration Y-domain
          />
        </div>
      </div>

      {/* Right Column: Vitals */}
      <div className="bg-slate-800 rounded p-1 sm:p-2 h-full overflow-hidden">
        <VitalsDisplay scenario={scenario} />
      </div>
    </div>
  );
};
