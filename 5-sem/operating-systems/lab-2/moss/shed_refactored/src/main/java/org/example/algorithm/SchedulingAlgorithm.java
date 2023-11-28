package org.example.algorithm;

// Run() is called from Scheduling.main() and is where
// the scheduling algorithm written by the user resides.
// User modification should occur within the Run() function.

import org.example.process.Results;
import java.util.Vector;

public class SchedulingAlgorithm {

  public static Results run(int runtime, Vector processVector, Results result) {
    // Algorithm alg = new FirstComeFirstServed();
    Algorithm alg = new ShortestProcessNext();
    return alg.run(runtime, processVector, result);
  }
}
