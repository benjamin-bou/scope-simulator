import React, { useState, useEffect, useRef, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';
import type { Scenario } from '../types'; // Keep for scenarioId type checking
import { DATA_POINTS_COUNT, UPDATE_INTERVAL_MS, SAMPLES_PER_SECOND } from '../constants';

interface DataPoint {
  timestamp: number;
  value: number;
}

interface WaveformTraceProps {
  basePattern: number[];
  lineColor: string;
  targetRate: number; // For ECG/Pleth: BPM, For Resp: Breaths/min
  valueType: 'ecg' | 'pleth' | 'resp';
  scenarioId: string; // e.g. 'vf', 'asystole'
  yDomain: [number, number];
}

export const WaveformTrace: React.FC<WaveformTraceProps> = ({
  basePattern,
  lineColor,
  targetRate,
  valueType,
  scenarioId,
  yDomain,
}) => {
  const [waveData, setWaveData] = useState<DataPoint[]>(() =>
    Array(DATA_POINTS_COUNT).fill(null).map((_, i) => ({ timestamp: i, value: yDomain[0] + (yDomain[1] - yDomain[0]) / 2 }))
  );

  const globalTimestampRef = useRef<number>(DATA_POINTS_COUNT);
  
  // Refs for dynamic variations
  const currentCycleSamplesRef = useRef<number>(0); // How many samples this particular cycle (beat/breath) will take
  const cycleProgressRef = useRef<number>(0); // How many samples we are into the current cycle

  // Store props in refs to access latest values in interval without re-creating interval
  const propsRef = useRef({ basePattern, targetRate, valueType, scenarioId, yDomain });

  useEffect(() => {
    propsRef.current = { basePattern, targetRate, valueType, scenarioId, yDomain };
    // Reset cycle if essential props change, to start new pattern cleanly
    cycleProgressRef.current = 0;
    
    if (propsRef.current.targetRate > 0 && propsRef.current.basePattern.length > 0) {
        const baseSamplesPerCycle = (60 / propsRef.current.targetRate) * SAMPLES_PER_SECOND;
        currentCycleSamplesRef.current = baseSamplesPerCycle * (1 + (Math.random() - 0.5) * 0.1); // Initial variation
    } else {
        currentCycleSamplesRef.current = Infinity; // For flatline if rate is 0
    }
  }, [basePattern, targetRate, valueType, scenarioId, yDomain]);


  const generateNextPoint = useCallback(() => {
    const { 
      basePattern: currentBasePattern, 
      targetRate: currentTargetRate, 
      valueType: currentValueType, 
      scenarioId: currentScenarioId,
      yDomain: currentYDomain
    } = propsRef.current;

    let newValue = currentYDomain[0] + (currentYDomain[1] - currentYDomain[0]) / 2; // Default to middle of Y range

    if (currentValueType === 'ecg' && currentScenarioId === 'vf') {
      newValue = (Math.random() - 0.5) * (currentYDomain[1] - currentYDomain[0]) * 0.9; // VF specific random, scaled to Y-domain
    } else if (currentTargetRate === 0 || !currentBasePattern || currentBasePattern.length === 0 || (currentBasePattern.length === 1 && currentBasePattern[0] === 0)) {
      // Asystole, apnea, or flatline pattern
      if (currentBasePattern && currentBasePattern.length === 1) {
          newValue = currentBasePattern[0];
      } else {
          // Default to 0 or center of Y domain if pattern implies flat but isn't explicitly [0]
          newValue = (currentYDomain[0] + currentYDomain[1]) / 2; 
          if (currentValueType === 'ecg' && currentScenarioId === 'asystole') newValue = 0; // ECG asystole specific
      }
    } else if (currentBasePattern.length > 0 && currentCycleSamplesRef.current > 0 && currentCycleSamplesRef.current !== Infinity) {
      const patternIndexFloat = (cycleProgressRef.current / currentCycleSamplesRef.current) * currentBasePattern.length;
      const patternIndex = Math.floor(patternIndexFloat) % currentBasePattern.length;
      
      newValue = currentBasePattern[patternIndex];

      // Amplitude variation: +/- 5%
      const amplitudeVariationFactor = 1 + (Math.random() - 0.5) * 0.10;
      newValue *= amplitudeVariationFactor;

      cycleProgressRef.current += 1;

      if (cycleProgressRef.current >= currentCycleSamplesRef.current) {
        cycleProgressRef.current = 0; // Reset for next cycle
        
        if (currentTargetRate > 0) { // Avoid division by zero if rate somehow becomes 0 mid-logic
            const baseSamplesPerCycle = (60 / currentTargetRate) * SAMPLES_PER_SECOND;
            // Rate variation: +/- 5% for ECG/Pleth, +/- 2.5% for Resp period
            const periodVariationPercentage = (currentValueType === 'resp') ? 0.05 : 0.10;
            const periodVariationFactor = 1 + (Math.random() - 0.5) * periodVariationPercentage;
            currentCycleSamplesRef.current = Math.max(SAMPLES_PER_SECOND / 10, baseSamplesPerCycle * periodVariationFactor); // Ensure not too fast
        } else {
            currentCycleSamplesRef.current = Infinity; // Rate became 0, go flat
        }
      }
    }
    // Clamp value to yDomain to prevent extreme variations from breaking chart
    newValue = Math.max(currentYDomain[0], Math.min(currentYDomain[1], newValue));

    setWaveData(prevData => {
      const newData = prevData.slice(1);
      newData.push({ timestamp: globalTimestampRef.current, value: newValue });
      globalTimestampRef.current += 1;
      return newData;
    });
  }, []); // Dependencies are handled by propsRef

  useEffect(() => {
    const intervalId = setInterval(generateNextPoint, UPDATE_INTERVAL_MS);
    return () => clearInterval(intervalId);
  }, [generateNextPoint]);

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={waveData} margin={{ top: 5, right: 5, left: -35, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={true} vertical={false} />
        <XAxis dataKey="timestamp" hide={true} type="number" domain={['dataMin', 'dataMax']} />
        <YAxis 
          type="number" 
          domain={yDomain}
          tickCount={5}
          stroke="#4b5563"
          axisLine={false}
          tickLine={false}
          width={30}
        />
        <Tooltip wrapperClassName="hidden" />
        <Line
          type="monotone"
          dataKey="value"
          className={lineColor}
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
