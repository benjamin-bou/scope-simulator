export interface Scenario {
  id: string;
  name: string;
  bpm: number; 
  basePattern: number[];
  lineColor: string; 
  textColor: string; 
  
  spo2?: number;
  plethBasePattern?: number[];
  plethLineColor?: string;
  plethTextColor?: string;

  respRate?: number;
  respBasePattern?: number[];
  respLineColor?: string;
  respTextColor?: string;
  
  nibp?: { systolic: number, diastolic: number };
}
