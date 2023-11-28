package org.example.process;

// This class represents the results of the scheduling simulation.
public class Results {
  // The type of scheduling algorithm used.
  public String schedulingType;
  // The name of the scheduling algorithm used.
  public String schedulingName;
  // The total computation time of the simulation.
  public int compuTime;

  // Constructor for the Results class.
  public Results(String schedulingType, String schedulingName, int compuTime) {
    this.schedulingType = schedulingType;
    this.schedulingName = schedulingName;
    this.compuTime = compuTime;
  }
}
