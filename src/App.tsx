
import React, { useState, useEffect, useCallback } from 'react';
import { ScopeDisplay } from './components/scope';
import { SCENARIOS, DEFAULT_SCENARIO_INDEX } from './constants';
import type { Scenario } from './types';

const App: React.FC = () => {
  const [currentScenario, setCurrentScenario] = useState<Scenario>(SCENARIOS[DEFAULT_SCENARIO_INDEX]);
  const [showHint, setShowHint] = useState<boolean>(false);

  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    if (event.key >= '1' && event.key <= String(SCENARIOS.length)) {
      const scenarioIndex = parseInt(event.key) - 1;
      if (scenarioIndex >= 0 && scenarioIndex < SCENARIOS.length) {
        setCurrentScenario(SCENARIOS[scenarioIndex]);
        setShowHint(true);
        setTimeout(() => setShowHint(false), 2000); // Show hint for 2 seconds
      }
    } else if (event.key.toLowerCase() === 'h') { // Toggle hint with 'h' key
        setShowHint(prev => !prev);
    }
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleKeyPress]);

  return (
    <div className="w-full h-full bg-slate-900 flex flex-col items-center justify-center p-4 select-none">
      <ScopeDisplay scenario={currentScenario} />
      {showHint && (
         <div className="absolute bottom-4 right-4 bg-slate-800 text-slate-400 p-3 rounded-md shadow-lg text-sm">
            <p className="font-semibold">Scénario Actuel: {currentScenario.name}</p>
            <p className="mt-1">Appuyez sur les touches 1-{SCENARIOS.length} pour changer de scénario.</p>
            <p className="mt-1">Appuyez sur 'H' pour afficher/cacher cette aide.</p>
        </div>
      )}
       <div className="absolute top-2 left-2 text-xs text-slate-600 font-mono">
          Simulateur de Scope Médical v1.0
      </div>
      <div className="absolute bottom-2 left-2 text-xs text-slate-700">
        Contrôles Professeur: Touches 1-{SCENARIOS.length} pour scénarios. 'H' pour aide.
      </div>
    </div>
  );
};

export default App;
    