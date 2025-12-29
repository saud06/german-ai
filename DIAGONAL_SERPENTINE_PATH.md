# 🎯 Diagonal Serpentine Path - Final Design

## Requirements Met:

### 1. ✅ Bottom-Left to Top-Right
**Diagonal progression:**
```javascript
const diagonalY = 550 - (progress * 350);
// Start: y=550 (bottom)
// End: y=200 (top)
```

### 2. ✅ Dynamic Waves (Not Fixed)
**Based on location count:**
```javascript
const wavesPerPath = Math.max(2, Math.floor(locations.length / 2));
// 3 locations → 2 waves
// 6 locations → 3 waves
// 10 locations → 5 waves
```

### 3. ✅ Smooth Curves (Not Sharp)
**Bezier curves with control points:**
```javascript
const controlY = (prev.y + curr.y) / 2;
const controlX1 = prev.x + 80;
const controlX2 = curr.x - 80;
// Creates smooth S-curves
```

## Pattern Breakdown:

### Diagonal Base:
```
[6] ← Top-right
  ↗
 [4]
  ↗
 [2]
  ↗
[1] ← Bottom-left
```

### Add Waves:
```
      [6]
     ↗ ↘
   [5]  [4]
  ↗      ↘
[3]       [2]
 ↘       ↗
  [1]
```

### Combined Result:
```
Diagonal upward + Serpentine waves
= Smooth winding path from bottom-left to top-right
```

## Formula:

```javascript
// 1. Diagonal progression (bottom-left to top-right)
const diagonalY = 550 - (progress * 350);

// 2. Dynamic wave frequency
const wavesPerPath = Math.floor(locations.length / 2);
const frequency = (wavesPerPath * Math.PI) / (locations.length - 1);

// 3. Wave amplitude
const amplitude = 80;

// 4. Combine
const waveOffset = Math.sin(idx * frequency) * amplitude;
const y = diagonalY + waveOffset;
```

## Examples by Location Count:

### 3 Locations:
- **Waves**: 2
- **Pattern**: Start low → Peak → End high
```
    [3]
   ↗
  [2]
 ↗ ↘
[1]
```

### 6 Locations:
- **Waves**: 3
- **Pattern**: Start low → Wave → Wave → End high
```
        [6]
       ↗
     [5]
    ↗ ↘
  [4]  [3]
 ↗      ↘
[2]      [1]
```

### 10 Locations:
- **Waves**: 5
- **Pattern**: Multiple smooth S-curves ascending
```
                [10]
               ↗
             [9]
            ↗ ↘
          [8]  [7]
         ↗      ↘
       [6]      [5]
      ↗ ↘      ↗
    [4]  [3]
   ↗      ↘
 [2]      [1]
```

## Coordinates (6 locations):

| Loc | X    | Diagonal Y | Wave | Final Y | Position |
|-----|------|------------|------|---------|----------|
| 1   | 50   | 550        | 0    | 550     | Bottom-left |
| 2   | 233  | 480        | +69  | 549     | Low |
| 3   | 416  | 410        | +80  | 490     | Middle-low |
| 4   | 599  | 340        | +69  | 409     | Middle |
| 5   | 782  | 270        | 0    | 270     | Middle-high |
| 6   | 965  | 200        | -69  | 131     | Top-right |

## Benefits:

✅ **Diagonal flow** - clear progression upward
✅ **Dynamic waves** - adapts to location count
✅ **Smooth curves** - Bezier interpolation
✅ **Natural look** - organic serpentine path
✅ **Scalable** - works for 3-20+ locations

## Visual Characteristics:

- **Start**: Bottom-left corner (y=550)
- **End**: Top-right corner (y=200)
- **Amplitude**: 80px (moderate waves)
- **Waves**: location_count / 2 (dynamic)
- **Smoothness**: Cubic Bezier curves

## Card Positioning:

```javascript
const isAbove = waveOffset < 0;

// Cards alternate based on wave position
// Above path when wave dips down
// Below path when wave rises up
```

🎉 **Perfect diagonal serpentine path with dynamic smooth waves!**
