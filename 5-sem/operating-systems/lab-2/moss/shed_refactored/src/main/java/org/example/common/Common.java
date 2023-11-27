package org.example.common;

import org.jetbrains.annotations.NotNull;

public class Common {

  static public int parseInt(@NotNull String s) {
    int i = 0;

    try {
      i = Integer.parseInt(s.trim());
    } catch (NumberFormatException nfe) {
      System.out.println("NumberFormatException: " + nfe.getMessage());
    }
    return i;
  }

  static public double parseDouble(@NotNull String s) {
    double d = 0.0;

    try {
      d = Double.parseDouble(s.trim());
    } catch (NumberFormatException nfe) {
      System.out.println("NumberFormatException: " + nfe.getMessage());
    }
    return d;
  }

  static public double RandomDouble() {
    java.util.Random generator = new java.util.Random(System.currentTimeMillis());
    double U = generator.nextDouble();
      double V = generator.nextDouble();
      double X =  Math.sqrt((8/Math.E)) * (V - 0.5)/U;
    if (!(RandomBoolean(X,U))) { return -1; }
    if (!(RandomBooleanTwo(X,U))) { return -1; }
    if (!(RandomBooleanThree(X,U))) { return -1; }
    return X;
  }

  static public boolean RandomBoolean(double X, double U) {
      return (X * X) <= (5 - 4 * Math.exp(.25) * U);
  }

  static public boolean RandomBooleanTwo(double X, double U) {
      return !((X * X) >= (4 * Math.exp(-1.35) / U + 1.4));
  }

  static public boolean RandomBooleanThree(double X, double U) {
      return (X * X) < (-4 * Math.log(U));
  }

}

