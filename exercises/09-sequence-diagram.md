# 9. Sequence diagram (LLM Architecture deck)

Draw a sequence diagram showing which components interact, and in what order, to set the speed limit.

## Round 1

![Round 1 sequence diagram for setting the speed limit](images/09-round1-sequence-diagram.png)

- If a road reading is missing, use 60 km/h as the road limit.
- If the LLM fails, skip the air-quality reduction and show a warning.
- The control room can override the result.

## Round 2

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "18px", "actorBkg": "#1e3a5f", "actorBorder": "#5b9bd5", "actorTextColor": "#ffffff", "actorLineColor": "#8a96a3", "signalColor": "#3b82f6", "signalTextColor": "#3b82f6", "labelBoxBkgColor": "#1e3a5f", "labelBoxBorderColor": "#5b9bd5", "labelTextColor": "#ffffff", "loopTextColor": "#3b82f6", "noteBkgColor": "#fff4c2", "noteBorderColor": "#d4a72c", "noteTextColor": "#1f2937", "sequenceNumberColor": "#ffffff"}, "sequence": {"useMaxWidth": false, "actorFontSize": 18, "messageFontSize": 17, "noteFontSize": 16}}}%%
sequenceDiagram
    autonumber
    participant Op as HighwayOperator
    participant SLS as SpeedLimitSoftware
    participant Sens as Sensors
    participant NN as NeuralNetwork
    participant AQ as AirQualityAPI
    participant LLM as LLM
    participant Sign as SpeedLimitSigns

    loop periodically (every update cycle)
        SLS->>Sens: readSensorData()
        Sens-->>SLS: water, light, temperature, wind, humidity, noise, traffic
        SLS->>SLS: evaluate(isDark, isWeatherBad)

        opt it is dark or weather is bad
            SLS->>NN: predictReduction(sensorData, currentLimit)
            NN-->>SLS: reductionNN (km/h)
        end

        SLS->>AQ: getCurrentAirQuality()
        AQ-->>SLS: airQualityData

        SLS->>LLM: assessAirQuality(airQualityData, currentLimit)
        LLM-->>SLS: isAirQualityBad, reductionAir (km/h)

        alt it is dark or weather is bad or air quality is bad
            SLS->>SLS: newLimit = 80 - max(reductionNN, reductionAir)
        else not dark, weather good and air quality good
            SLS->>SLS: newLimit = 80
        end

        SLS->>Sign: setSpeedLimit(newLimit)
        Sign-->>SLS: confirmation
    end

    Note over SLS: Sensor, limit and accident/near-accident data are also stored as records for offline machine learning analysis, not used in this production flow.
```

Note: if you want the LLM call to happen only when needed, it can be placed in an `opt` as well. As drawn, air quality is queried every cycle because the task states that it is an independent reason to reduce the limit.

## Round 3

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "18px", "actorBkg": "#1e3a5f", "actorBorder": "#5b9bd5", "actorTextColor": "#ffffff", "actorLineColor": "#8a96a3", "signalColor": "#3b82f6", "signalTextColor": "#3b82f6", "labelBoxBkgColor": "#1e3a5f", "labelBoxBorderColor": "#5b9bd5", "labelTextColor": "#ffffff", "loopTextColor": "#3b82f6", "noteBkgColor": "#fff4c2", "noteBorderColor": "#d4a72c", "noteTextColor": "#1f2937", "sequenceNumberColor": "#ffffff"}, "sequence": {"useMaxWidth": false, "actorFontSize": 18, "messageFontSize": 17, "noteFontSize": 16}}}%%
sequenceDiagram
    autonumber
    participant CR as Control room
    participant GUI
    participant AQ as Air quality client
    participant SD as Speed limit decider
    participant RO as Router
    participant NP as Network predictor
    participant LA as LLM advisor
    participant LOG as Decision log

    CR->>GUI: Set speed limit
    GUI->>AQ: fetch_air_quality()
    AQ-->>GUI: AQI
    GUI->>SD: set_speed_limit(readings, AQI, override)

    alt a reading is missing
        Note over SD: road limit 60 km/h and a warning
    else all readings there
        SD->>RO: is_dark(), has_black_ice_risk()
        RO-->>SD: yes or no
        opt dark or icy
            loop 40, 50, 60 and 70 km/h
                SD->>NP: predict_near_accidents(readings, limit)
                NP-->>SD: near-accidents per hour
            end
            Note over SD: highest limit with at most 1, otherwise 40 km/h and a warning
        end
    end

    SD->>LA: decide_reduction(AQI)
    opt AQI above 40
        Note over LA: asks Gemini for 10, 20, 30 or 40 km/h
    end
    LA-->>SD: reduction (0 if AQI 40 or below, none and a warning if Gemini fails)

    SD-->>GUI: lower limit wins (80 km/h if nothing applies, override replaces it) and warnings
    GUI->>LOG: log_decision()
    GUI-->>CR: show the limit and any warnings
```

## Comparison

For Round 1, I drew one example the way the lecture does: a dark, icy hour with an AQI of 95, with the real function names from our code and the actual values. It's simple and easy to read, and you can follow it from the click to the final 40 km/h.

The AI rounds made the diagram more complex and used more technical language than I did. Round 2 used loop, opt and alt boxes for the conditions, but it put the whole system into one SpeedLimitSoftware box, added parts we don't have, like the road signs, and its network returns a reduction instead of predicting near-accidents.

Round 3 kept those boxes but was more to the point. It used our own components from 08, dropped the parts we don't have, and showed the network predicting near-accidents for each limit. It's the most accurate of the three, but still more technical and harder to read than mine.

What I learnt: the AI is good at covering every case in the right notation, but a simple example is easier to read and to explain.
