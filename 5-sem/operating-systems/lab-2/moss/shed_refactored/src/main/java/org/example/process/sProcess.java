package org.example.process;

import org.example.common.Common;

public class sProcess {
  public int cputime;
  public int ioblocking;
  public int cpudone;
  public int ionext;
  public int numblocked;
  public int standIoblockingDev;

  // aging variables
  public double alpha;
  public int estimatedExecutionTime;

  public sProcess(int cputime, int ioblocking, int cpudone, int ionext, int numblocked) {
    this.cputime = cputime;
    this.ioblocking = ioblocking;
    this.cpudone = cpudone;
    this.ionext = ionext;
    this.numblocked = numblocked;
  }

  public void setAlpha(double alpha) {
    this.alpha = alpha;
  }

  public void setStandIoblockingDev(int standIoblockingDev) {
    this.standIoblockingDev = standIoblockingDev;
  }

  public void calculateEstimateExecutionTime() {
    estimatedExecutionTime = (int) (alpha * ioblocking + (1 - alpha) * estimatedExecutionTime);
  }

  public void calculateIoBlocking() {
    double X = Common.R1();
    while (X == -1.0) {
      X = Common.R1();
    }
    X = X * standIoblockingDev;
    this.ioblocking = (int) X + ioblocking;
  }
}
