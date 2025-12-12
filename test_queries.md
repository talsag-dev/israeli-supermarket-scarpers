# Complex Test Queries for Manual Testing

This document contains a comprehensive set of complex queries to test the LLM-powered natural language to SQL system.

## 1. Geographic & Regional Queries

### 1.1 Region-Based Queries (Testing REGION_MAPPING)
```
מה המחיר הממוצע של חלב במרכז?
```
**Expected behavior**: Should expand "מרכז" to all cities in the center region using `IN` clause

```
תן לי את 10 החנויות הזולות ביותר בצפון
```
**Expected behavior**: Should search across all northern cities

```
השווה מחירי במבה בין הדרום למרכז
```
**Expected behavior**: Should compare prices between two regions

### 1.2 Specific City Queries
```
מצא את החנות הזולה ביותר לקניות בתל אביב-יפו
```

```
כמה חנויות יש בירושלים?
```

```
תן לי רשימה של כל החנויות בחיפה ובאר שבע
```

## 2. Product Search & Price Comparison

### 2.1 Specific Product Queries
```
מה המחיר של במבה בכל הרשתות?
```

```
איפה הכי זול לקנות חלב 3%?
```

```
תן לי את 5 המוצרים הכי יקרים במאפיות
```

### 2.2 Partial Match Queries
```
תן לי את כל המוצרים שמכילים "שוקולד"
```

```
מצא לי מוצרים של תנובה
```

```
חפש מוצרים עם המילה "אורגני"
```

### 2.3 Price Range Queries
```
תן לי מוצרים שעולים בין 10 ל-20 שקלים
```

```
מה המוצרים הכי זולים (מתחת ל-5 שקלים)?
```

## 3. Aggregation & Statistics

### 3.1 Average Prices
```
מה המחיר הממוצע של מוצרי חלב?
```

```
תן לי את המחיר הממוצע לפי רשת
```

```
מה ההפרש בין המחיר הממוצע במרכז לדרום?
```

### 3.2 Count & Group By
```
כמה מוצרים יש לכל יצרן?
```

```
תן לי את מספר החנויות לפי עיר
```

```
מה הרשת עם הכי הרבה חנויות?
```

### 3.3 Min/Max Queries
```
מה המוצר הכי יקר בכל רשת?
```

```
תן לי את המחיר המינימלי והמקסימלי של במבה
```

```
איזו חנות מוכרת את הלחם הכי זול?
```

## 4. Multi-Table Joins

### 4.1 Store + Price Joins
```
תן לי את המחיר של קוקה קולה בכל חנות בתל אביב
```

```
מצא את החנות עם המחיר הנמוך ביותר לביסלי בכל עיר
```

```
השווה מחירים של אותו מוצר בין חנויות שונות באותה עיר
```

### 4.2 Complex Joins with Aggregations
```
תן לי את הרשת עם המחיר הממוצע הנמוך ביותר למוצרי חלב
```

```
מה העיר עם המחיר הממוצע הגבוה ביותר?
```

```
תן לי את 3 הרשתות הזולות ביותר בממוצע
```

## 5. Time-Based Queries

### 5.1 Recent Data
```
תן לי מחירים שעודכנו בשבוע האחרון
```

```
מה המוצרים שעודכנו היום?
```

```
תן לי את המחירים העדכניים ביותר של חלב
```

### 5.2 Date Range Queries
```
תן לי מחירים מהחודש האחרון
```

```
השווה מחירים בין השבוע הזה לשבוע שעבר
```

## 6. Promotions

### 6.1 Active Promotions
```
מה המבצעים הפעילים כרגע?
```

```
תן לי מבצעים שמסתיימים השבוע
```

```
מה המבצעים על מוצרי חלב?
```

### 6.2 Promotion Details
```
תן לי את כל המבצעים שמתחילים היום
```

```
מצא מבצעים שנמשכים יותר משבועיים
```

## 7. Complex Multi-Criteria Queries

### 7.1 Combined Filters
```
תן לי מוצרים של תנובה שעולים פחות מ-15 שקלים בתל אביב
```

```
מצא חנויות ברמת גן שמוכרות במבה במחיר נמוך מ-5 שקלים
```

```
תן לי את 10 המוצרים הזולים ביותר של אוסם שעודכנו השבוע
```

### 7.2 Ranking & Top N
```
תן לי את 5 החנויות הזולות ביותר לקניות במרכז
```

```
מה 10 המוצרים הכי פופולריים (לפי מספר חנויות שמוכרות אותם)?
```

```
תן לי את 3 הרשתות עם המחירים הנמוכים ביותר בממוצע
```

## 8. Edge Cases & Tricky Queries

### 8.1 Ambiguous Queries
```
תן לי מוצרים זולים
```
**Challenge**: No specific price threshold defined

```
מה החנויות הטובות?
```
**Challenge**: "טובות" is subjective

```
תן לי מידע על שוקולד
```
**Challenge**: Very broad, unclear what information is needed

### 8.2 Null/Missing Data Handling
```
תן לי מוצרים ללא יצרן
```

```
מצא חנויות ללא כתובת
```

```
תן לי מוצרים עם מחיר 0
```

### 8.3 Case Sensitivity & Hebrew
```
תן לי מוצרים של תנובה
```
**Should use**: `ilike` for case-insensitive matching

```
מצא מוצרים עם "במבה" או "ביסלי"
```

```
חפש חנויות עם "סופר" בשם
```

### 8.4 Special Characters & Encoding
```
תן לי מוצרים עם % בשם
```

```
מצא מוצרים עם "3%" בשם
```

## 9. Performance Testing Queries

### 9.1 Large Result Sets
```
תן לי את כל המוצרים במאגר
```
**Should limit**: To 100 rows as per schema rules

```
תן לי את כל החנויות בישראל
```

### 9.2 Complex Aggregations
```
תן לי את המחיר הממוצע, המינימלי והמקסימלי לכל מוצר
```

```
חשב את סטיית התקן של מחירי החלב
```

## 10. Business Intelligence Queries

### 10.1 Market Analysis
```
איזו רשת הכי יקרה בממוצע?
```

```
מה ההפרש במחירים בין הרשת הזולה ביותר ליקרה ביותר?
```

```
תן לי את התפלגות המחירים של במבה
```

### 10.2 Competitive Analysis
```
השווה את המחירים של שופרסל לרמי לוי
```

```
באיזו עיר יש את התחרות הכי גדולה (מספר חנויות)?
```

```
מה הרשת עם המגוון הגדול ביותר של מוצרים?
```

## 11. Validation & Data Quality

### 11.1 Data Consistency
```
תן לי מוצרים עם אותו ItemCode אבל מחירים שונים
```

```
מצא חנויות עם StoreId כפול
```

```
תן לי מוצרים עם כמות שלילית
```

### 11.2 Outlier Detection
```
תן לי מוצרים עם מחיר חריג (יותר מ-1000 שקלים)
```

```
מצא חנויות עם מספר מוצרים חריג
```

## 12. Natural Language Variations

### 12.1 Different Phrasings
```
כמה עולה במבה?
```

```
מחיר של במבה
```

```
במבה - מחיר
```

```
רוצה לדעת כמה עולה במבה
```

### 12.2 Conversational Style
```
אני מחפש את החנות הכי זולה לקניות שלי
```

```
תגיד לי איפה כדאי לקנות חלב
```

```
מעניין אותי לדעת מה המחיר של קוקה קולה
```

---

## Testing Checklist

- [ ] All region-based queries expand correctly to city lists
- [ ] Partial matches use `ilike` correctly
- [ ] All queries use fully qualified table names
- [ ] Results are limited to 100 rows
- [ ] Joins use correct syntax
- [ ] Hebrew text is handled correctly
- [ ] Case-insensitive searches work
- [ ] Date/time queries work correctly
- [ ] Aggregations produce correct results
- [ ] Edge cases are handled gracefully
- [ ] LLM returns only SQL (no markdown/explanations)
- [ ] Invalid queries return helpful error messages
