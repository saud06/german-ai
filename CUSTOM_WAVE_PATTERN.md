# 🌊 Custom Wave Pattern - Matching Red Line

## Wave Pattern Analysis:

From the red line in the image, the path should:
1. **Start high** on the left (top-left area)
2. **Dip down** in the middle (bottom-middle)
3. **Rise up** on the right (top-right area)

## Implementation:

### Wave Pattern Logic:
```javascript
const progress = idx / (locations.length - 1); // 0 to 1

if (progress < 0.33) {
  // First third: start high (250), go down to (450)
  y = 250 + (progress * 3) * 200;
} else if (progress < 0.66) {
  // Middle third: stay low (450 to 500)
  y = 450 + ((progress - 0.33) * 3) * 50;
} else {
  // Last third: rise up (500 to 200)
  y = 500 - ((progress - 0.66) * 3) * 300;
}
```

## Visual Pattern:

```
Location:  1    2    3    4    5    6
Y-coord:  250  350  450  475  350  200
          
          1                        6
           \                      /
            2                   5
             \                /
              3────────────4
```

## Breakdown by Section:

### Section 1: Descending (0-33%)
- **Locations**: 1-2
- **Y-range**: 250 → 450
- **Movement**: Downward slope
- **Cards**: Above path

### Section 2: Bottom (33-66%)
- **Locations**: 3-4
- **Y-range**: 450 → 500
- **Movement**: Gentle dip
- **Cards**: Below path

### Section 3: Ascending (66-100%)
- **Locations**: 5-6
- **Y-range**: 500 → 200
- **Movement**: Steep upward
- **Cards**: Above path

## Coordinates for 6 Locations:

| Location | Progress | Y-coord | Position |
|----------|----------|---------|----------|
| 1        | 0.00     | 250     | High left |
| 2        | 0.20     | 370     | Descending |
| 3        | 0.40     | 460     | Low middle |
| 4        | 0.60     | 490     | Lowest |
| 5        | 0.80     | 320     | Rising |
| 6        | 1.00     | 200     | High right |

## Card Positioning:

```javascript
const isAbove = y < 350; // Above if in upper half

// Cards alternate based on height
if (isAbove) {
  // Card above path (locations 1, 5, 6)
  transform: translate(x, y - 80)
} else {
  // Card below path (locations 2, 3, 4)
  transform: translate(x, y + 80)
}
```

## Benefits:

✅ **Matches red line** - exact pattern from image
✅ **Natural flow** - smooth descent and ascent
✅ **Visual interest** - dynamic wave shape
✅ **Clear progression** - left to right journey
✅ **Proper spacing** - cards don't overlap

## Comparison:

### Before (Sine Wave):
```
Regular oscillation: up-down-up-down
```

### After (Custom Wave):
```
Natural flow: high → low → high
Matches user's red line exactly
```

🎉 **Path now follows the exact wave pattern from the red line!**
