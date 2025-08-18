import React from 'react';
import type { Scenario } from '../types';
import { HeartIcon } from './icons/HeartIcon';

interface VitalSignProps {
  label: string;
  value: string | number;
  unit?: string;
  colorClass: string;
  icon?: React.ReactNode;
  valueSize?: string;
  labelSize?: string;
  unitSize?: string;
  className?: string;
}

const VitalSign: React.FC<VitalSignProps> = ({ 
  label, value, unit, colorClass, icon, 
  valueSize = 'text-3xl sm:text-4xl', 
  labelSize = 'text-xs sm:text-sm',
  unitSize = 'text-xs sm:text-sm',
  className = ''
}) => (
  <div className={`flex flex-row items-center justify-between p-2 ${className}`}>
    <div className="flex items-center">
      {icon && <span className={`mr-2 w-5 h-5 sm:w-6 sm:h-6 ${colorClass}`}>{icon}</span>}
      <div>
        <span className={`${labelSize} ${colorClass} font-medium`}>{label}</span>
        {unit && <span className={`ml-1 ${unitSize} ${colorClass} opacity-80`}>{unit}</span>}
      </div>
    </div>
    <div className={`${valueSize} font-bold ${colorClass} tabular-nums`}>
      {value}
    </div>
  </div>
);


export const VitalsDisplay: React.FC<{ scenario: Scenario }> = ({ scenario }) => {
  const displayBpm = scenario.id === 'vf' ? '---' : (scenario.bpm > 0 ? scenario.bpm : '0');
  
  let spo2Value: string | number = '---';
  if (scenario.spo2 !== undefined) {
    if (scenario.id === 'asystole' || (scenario.id === 'vf' && scenario.spo2 < 10) ) { // Very low SpO2 in VF might show as ---
      spo2Value = scenario.spo2 === 0 ? '0' : '---';
    } else {
      spo2Value = scenario.spo2;
    }
  }
  
  let respRateValue: string | number = '---';
  if (scenario.respRate !== undefined) {
     if (scenario.id === 'asystole' || (scenario.id === 'vf' && scenario.respRate === 0)) {
        respRateValue = '0';
     } else if (scenario.respRate > 0) {
        respRateValue = scenario.respRate;
     } else if (scenario.respRate === 0) {
        respRateValue = '0';
     }
  }


  const nibpValue = scenario.nibp ? 
    (scenario.nibp.systolic === 0 && scenario.nibp.diastolic === 0 && (scenario.id === 'asystole' || scenario.id === 'vf') ? '0/0' : `${scenario.nibp.systolic}/${scenario.nibp.diastolic}`)
    : '---';

  return (
    <div className="h-full w-full flex flex-col justify-around text-white font-sans py-1 sm:py-2">
      <VitalSign
        label="FC"
        value={displayBpm}
        unit="bpm"
        colorClass={scenario.textColor || 'text-green-400'}
        icon={<HeartIcon className={`w-full h-full`} />}
        valueSize="text-4xl sm:text-5xl"
      />
      <VitalSign
        label="SpO₂"
        value={spo2Value}
        unit="%"
        colorClass={scenario.plethTextColor || 'text-cyan-400'}
        icon={<span className="font-bold text-lg">🌊</span>} // Placeholder icon
        valueSize="text-4xl sm:text-5xl"
      />
      <VitalSign
        label="FR"
        value={respRateValue}
        unit="/min"
        colorClass={scenario.respTextColor || 'text-yellow-300'}
        icon={<span className="font-bold text-lg">〰️</span>} // Placeholder icon
        valueSize="text-4xl sm:text-5xl"
      />
      <VitalSign
        label="PNI"
        value={nibpValue}
        unit="mmHg"
        colorClass="text-lime-400" // NIBP has its own consistent color
        // No icon typically, or a generic one
        valueSize="text-3xl sm:text-4xl"
        className="pt-2" // Add some padding top for NIBP as it's often less critical rhythm-wise
      />
    </div>
  );
};
