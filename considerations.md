

/*


freeways:
0–500 Feet (The Red Zone): Not recommended. Air pollution levels (ultrafine particles, CO, and NOx) are at their highest.

500–1,000 Feet (The Caution Zone): The minimum recommended buffer. Pollution levels drop by about 70% by the 500-foot mark.

1,000 Feet to 1 Mile (The Optimal Zone): Health risks significantly diminish, though wind patterns can still carry pollutants into this range.

Distance: For a dialysis and oxygen user, aim for at least 1,500 to 2,000 feet (nearly half a mile) if possible. The cumulative stress of kidney failure and respiratory issues makes the body much less resilient to the "Red Zone" pollutants.



air ports/flight paths:
Dialysis/Oxygen Specifics: Because these conditions involve the blood and lungs directly, the "Optimal Zone" for this individual should be outside of the 5-mile radius whenever possible from an air port and flight paths.



flood:
"Zone A" or "Zone AE" are the 100-year floodplains (high risk)(especially Mission Valley).

Sanitary Issues: Floodwaters in San Diego (particularly the South Bay/Tijuana River area) are often contaminated with sewage. This is an extreme infection risk for someone with a dialysis shunt or compromised health.
*/


/*
  This query identifies areas to AVOID based on your proximity guide.
  Targeted for San Diego, CA.
  
  Buffers used:
  - Freeways/Major Roads: 610m (~2,000 ft)
  - Airports: 8000m (~5 miles)
  - River Corridors: 300m (Proxy for flood risk)
*/

/*
  This query identifies areas to AVOID based on your proximity guide.
  Targeted for San Diego, CA.
  
  Buffers used:
  - Freeways/Major Roads: 610m (~2,000 ft)
  - Airports: 8000m (~5 miles)
  - River Corridors: 300m (Proxy for flood risk)
*/


claude thoughts
The considerations in this file are very well-suited for someone in that situation. Here's my take:
The criteria are spot-on, and actually critically important for this person specifically:
Freeway buffer (2,000 ft) — This is a smart, conservative choice. For someone on supplemental oxygen, their lungs are already compromised and have almost no reserve to handle ultrafine particulate matter. The standard "caution zone" of 500 ft that might be fine for a healthy adult is genuinely dangerous here. The 2,000 ft buffer is the right call.
Airport/flight path buffer (5 miles) — Again appropriate. The combination of fine particles from jet exhaust and the noise stress (which raises blood pressure and cortisol) is a real concern. Chronic noise stress is hard on the cardiovascular system, which is already burdened by dialysis dependency.
Flood zone avoidance — This one is arguably the most critical consideration of all. A dialysis patient has a surgically placed shunt/fistula — an open pathway to the bloodstream. Flood exposure (especially in San Diego where Tijuana River contamination is a known, recurring problem) could mean a life-threatening infection. Evacuation during a flood event is also extremely difficult for someone on oxygen and requiring thrice-weekly dialysis. Being cut off from the dialysis center even for a day or two is dangerous.
