# SpacePoint Instructor Training – Task 1 Question Bank

## Question Bank Structure

This assessment bank contains **10 question categories**. Each category is based on one of the 10 questions in the original SpacePoint Instructor Training – Task 1 Assessment.

Each category contains **3 questions with the same question pattern and learning objective**:

- One original question
- Two alternative questions following the same format and difficulty

The assessment system should randomly select **one question from each category**, producing a final assessment of **10 questions**.

## Random Selection Rule

```text
For each category from Category 1 to Category 10:
    Randomly select one question from the three available questions.

Total questions selected per assessment: 10
```

---

# Category 1: Subsystem Block Diagram and Analysis

**Category ID:** `CAT-01`

**Selection Rule:** Randomly select one of the following three questions.

## Question 1.1 – CubeSat EPS Block Diagram

**Question ID:** `CAT-01-Q01`

**Task:** Draw a block diagram of a typical CubeSat Electrical Power System (EPS).

**Follow-up Question:** After creating your diagram, identify which critical component might be missing and explain why it is essential for safe and efficient power distribution.

---

## Question 1.2 – CubeSat CDHS Block Diagram

**Question ID:** `CAT-01-Q02`

**Task:** Draw a block diagram of a typical CubeSat Command and Data Handling System (CDHS). Include the onboard computer, memory devices, payload interface, subsystem interfaces, and communication links.

**Follow-up Question:** After creating your diagram, identify one possible single point of failure and explain how the design could be improved to increase reliability.

---

## Question 1.3 – CubeSat ADCS Block Diagram

**Question ID:** `CAT-01-Q03`

**Task:** Draw a block diagram of a typical CubeSat Attitude Determination and Control System (ADCS). Include attitude sensors, the onboard processor, control algorithms, and actuators.

**Follow-up Question:** After creating your diagram, identify one critical sensor or actuator whose failure could significantly affect the system and explain why.

---

# Category 2: Subsystem Sizing and Engineering Calculation

**Category ID:** `CAT-02`

**Selection Rule:** Randomly select one of the following three questions.

## Question 2.1 – Sizing Solar Panels

**Question ID:** `CAT-02-Q01`

**Scenario:** You have a CubeSat with a total average power consumption of 5 W in daylight and 2 W in eclipse.

**Question:** How would you size and select solar panels for this mission, considering orbital conditions and required safety margins?

---

## Question 2.2 – Sizing a CubeSat Battery

**Question ID:** `CAT-02-Q02`

**Scenario:** A CubeSat consumes an average of 4 W during a 35-minute eclipse. The battery operates at 7.4 V, and the mission limits the maximum depth of discharge to 30%.

**Question:** Calculate the minimum theoretical battery capacity required for one eclipse. Then explain what safety margin you would apply when selecting the actual battery.

---

## Question 2.3 – Sizing Onboard Data Storage

**Question ID:** `CAT-02-Q03`

**Scenario:** A CubeSat payload generates twelve images per orbit, with each image having a size of 5 MB. Housekeeping telemetry adds 3 MB per orbit. The satellite completes 15 orbits per day and may operate for two days without a successful downlink.

**Question:** Calculate the minimum onboard storage capacity required. Then recommend a suitable storage margin and explain why it is necessary.

---

# Category 3: Identifying the Most Critical Subsystem

**Category ID:** `CAT-03`

**Selection Rule:** Randomly select one of the following three questions.

## Question 3.1 – Critical System for Beacon Activation

**Question ID:** `CAT-03-Q01`

**Question:** If a satellite beacon is triggered via telecommand from the ground, which subsystem is most critical in ensuring the beacon can be activated successfully? Explain your reasoning.

---

## Question 3.2 – Critical System for Payload Image Capture

**Question ID:** `CAT-03-Q02`

**Question:** If a CubeSat must capture a payload image at a specific location and time, which subsystem is most critical in ensuring the image is captured successfully? Explain your reasoning and describe how it depends on other subsystems.

---

## Question 3.3 – Critical System for Safe-Mode Entry

**Question ID:** `CAT-03-Q03`

**Question:** If a CubeSat detects dangerously low battery voltage and must automatically enter Safe Mode, which subsystem is most critical in ensuring the response is executed successfully? Explain your reasoning.

---

# Category 4: Subsystem Anomaly Troubleshooting

**Category ID:** `CAT-04`

**Selection Rule:** Randomly select one of the following three questions.

## Question 4.1 – Identifying ADCS Anomalies

**Question ID:** `CAT-04-Q01`

**Scenario:** During a ground test, your Attitude Determination and Control System (ADCS) fails to maintain correct orientation.

**Question:** Propose a troubleshooting plan to isolate and fix the issue, considering both hardware and software factors.

---

## Question 4.2 – Diagnosing Repeated Onboard Computer Resets

**Question ID:** `CAT-04-Q02`

**Scenario:** During payload operation, the CubeSat onboard computer repeatedly resets. The resets do not occur when the payload is switched off.

**Question:** Propose a troubleshooting plan to isolate and fix the issue, considering power stability, electrical noise, software faults, watchdog behavior, and thermal conditions.

---

## Question 4.3 – Diagnosing Unstable EPS Output

**Question ID:** `CAT-04-Q03`

**Scenario:** During system testing, the EPS output voltage drops whenever the communication transmitter is activated, causing other subsystems to behave unpredictably.

**Question:** Propose a troubleshooting plan to isolate and fix the issue, considering the battery, voltage regulators, wiring, current demand, grounding, and power-distribution design.

---

# Category 5: Environmental and Qualification Test Planning

**Category ID:** `CAT-05`

**Selection Rule:** Randomly select one of the following three questions.

## Question 5.1 – Devising a Thermal Cycling Test

**Question ID:** `CAT-05-Q01`

**Scenario:** Your team suspects the satellite’s payload is highly sensitive to extreme temperature swings.

**Question:** Design a simple thermal cycling test plan and justify the temperature ranges, duration of tests, and expected outcomes.

---

## Question 5.2 – Devising a Vibration Test

**Question ID:** `CAT-05-Q02`

**Scenario:** Your team must verify that a fully assembled CubeSat can survive the launch environment without structural or electrical failure.

**Question:** Design a basic vibration test plan and justify the tested axes, test sequence, functional checks, inspection stages, and pass/fail criteria.

---

## Question 5.3 – Devising a Communication Range Test

**Question ID:** `CAT-05-Q03`

**Scenario:** Your team must verify that the CubeSat communication system can maintain a reliable link under different distances, antenna orientations, and interference conditions.

**Question:** Design a communication range test plan and justify the distances, test configurations, measurements, repetition count, and expected outcomes.

---

# Category 6: Mission Risk Identification and Mitigation

**Category ID:** `CAT-06`

**Selection Rule:** Randomly select one of the following three questions.

## Question 6.1 – Risks in Low Earth Orbit

**Question ID:** `CAT-06-Q01`

**Question:** List three major risks that small satellites face in Low Earth Orbit (LEO). Suggest at least one specific mitigation strategy for each risk and explain why you chose those strategies.

---

## Question 6.2 – Risks During CubeSat Launch and Deployment

**Question ID:** `CAT-06-Q02`

**Question:** List three major risks that a CubeSat faces during launch, separation, and early orbit operations. Suggest at least one specific mitigation strategy for each risk and explain why you chose those strategies.

---

## Question 6.3 – Risks During Ground Operations

**Question ID:** `CAT-06-Q03`

**Question:** List three major risks that could affect CubeSat ground operations and mission control. Suggest at least one specific mitigation strategy for each risk and explain why you chose those strategies.

---

# Category 7: Failed Mission or Subsystem Evaluation

**Category ID:** `CAT-07`

**Selection Rule:** Randomly select one of the following three questions.

## Question 7.1 – Evaluating a Communication Subsystem Failure

**Question ID:** `CAT-07-Q01`

**Scenario:** You have found a case study where a CubeSat failed due to communication subsystem issues.

**Question:** How would you restructure the CubeSat’s communication subsystem design or operational procedures to prevent a similar failure in future missions?

---

## Question 7.2 – Evaluating an EPS Failure

**Question ID:** `CAT-07-Q02`

**Scenario:** You have found a case study where a CubeSat mission ended early because the batteries could not maintain sufficient charge during eclipse periods.

**Question:** How would you restructure the CubeSat’s EPS design or operational procedures to prevent a similar failure in future missions?

---

## Question 7.3 – Evaluating an ADCS Failure

**Question ID:** `CAT-07-Q03`

**Scenario:** You have found a case study where a CubeSat could not complete its mission because it failed to achieve stable attitude control after deployment.

**Question:** How would you restructure the CubeSat’s ADCS design, testing process, or operational procedures to prevent a similar failure in future missions?

---

# Category 8: Concept of Operations Development

**Category ID:** `CAT-08`

**Selection Rule:** Randomly select one of the following three questions.

## Question 8.1 – Magnetic-Field Mission ConOps

**Question ID:** `CAT-08-Q01`

**Question:** If you were to draft a Concept of Operations for a 3U CubeSat studying Earth’s magnetic field, what mission phases would you include and why? Be specific about data collection, communication windows, and power management.

---

## Question 8.2 – Earth-Imaging Mission ConOps

**Question ID:** `CAT-08-Q02`

**Question:** If you were to draft a Concept of Operations for a 3U Earth-imaging CubeSat, what mission phases would you include and why? Be specific about target selection, attitude control, image capture, data storage, downlink windows, and power management.

---

## Question 8.3 – Space-Weather Mission ConOps

**Question ID:** `CAT-08-Q03`

**Question:** If you were to draft a Concept of Operations for a CubeSat monitoring space-weather conditions, what mission phases would you include and why? Be specific about sensor activation, data collection frequency, onboard processing, communication windows, and Safe Mode behavior.

---

# Category 9: Ground-Station Data Interpretation and Diagnosis

**Category ID:** `CAT-09`

**Selection Rule:** Randomly select one of the following three questions.

## Question 9.1 – Intermittent Data Loss and Signal Variation

**Question ID:** `CAT-09-Q01`

**Scenario:** Your ground station logs indicate intermittent data loss and unexpected signal-strength variations.

**Question:** What factors could be causing these issues, and how would you systematically diagnose and resolve them?

---

## Question 9.2 – Beacon Received but No Telemetry Decoded

**Question ID:** `CAT-09-Q02`

**Scenario:** Your ground station detects the CubeSat beacon during each pass, but the telemetry packets cannot be decoded correctly.

**Question:** What factors could be causing this issue, and how would you systematically diagnose and resolve it using ground-station logs, radio settings, packet configuration, and onboard information?

---

## Question 9.3 – Expected Pass but No Signal Received

**Question ID:** `CAT-09-Q03`

**Scenario:** The orbit-prediction software shows that the CubeSat is passing directly over the ground station, but no signal is received during the predicted communication window.

**Question:** What factors could be causing this issue, and how would you systematically diagnose and resolve it?

---

# Category 10: Space Mission Case Study and Improvement

**Category ID:** `CAT-10`

**Selection Rule:** Randomly select one of the following three questions.

## Question 10.1 – UAE Space Mission Insight

**Question ID:** `CAT-10-Q01`

**Task:** Choose one UAE CubeSat or satellite mission that interests you.

**Question:** How did the design of this mission’s subsystems reflect specific objectives or constraints? Propose one improvement or addition to enhance the mission’s success if it were re-launched today.

---

## Question 10.2 – International CubeSat Mission Insight

**Question ID:** `CAT-10-Q02`

**Task:** Choose one international CubeSat mission that interests you.

**Question:** How did the design of this mission’s subsystems reflect its scientific, educational, or commercial objectives? Propose one improvement or addition to enhance the mission’s success if it were re-launched today.

---

## Question 10.3 – Failed CubeSat Mission Insight

**Question ID:** `CAT-10-Q03`

**Task:** Choose one CubeSat mission that experienced a major anomaly, partial failure, or complete mission failure.

**Question:** How did the mission design, subsystem choices, testing process, or operational constraints contribute to the outcome? Propose one improvement or addition that could increase the likelihood of success if the mission were re-launched today.

---

# Category Summary for System Implementation

| Category ID | Question Pattern | Available Question IDs | Select |
|---|---|---|---:|
| `CAT-01` | Subsystem block diagram and analysis | `CAT-01-Q01` to `CAT-01-Q03` | 1 |
| `CAT-02` | Subsystem sizing and calculation | `CAT-02-Q01` to `CAT-02-Q03` | 1 |
| `CAT-03` | Identify the most critical subsystem | `CAT-03-Q01` to `CAT-03-Q03` | 1 |
| `CAT-04` | Subsystem anomaly troubleshooting | `CAT-04-Q01` to `CAT-04-Q03` | 1 |
| `CAT-05` | Environmental and qualification test plan | `CAT-05-Q01` to `CAT-05-Q03` | 1 |
| `CAT-06` | Mission risk and mitigation | `CAT-06-Q01` to `CAT-06-Q03` | 1 |
| `CAT-07` | Failed mission or subsystem evaluation | `CAT-07-Q01` to `CAT-07-Q03` | 1 |
| `CAT-08` | Concept of Operations development | `CAT-08-Q01` to `CAT-08-Q03` | 1 |
| `CAT-09` | Ground-station data interpretation | `CAT-09-Q01` to `CAT-09-Q03` | 1 |
| `CAT-10` | Mission case study and improvement | `CAT-10-Q01` to `CAT-10-Q03` | 1 |

**Total categories:** 10  
**Questions available per category:** 3  
**Total questions in the bank:** 30  
**Questions selected per assessment:** 10
