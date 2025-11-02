# 🔧 Guide: Create a Clash Test in ACC Model Coordination

## 📋 Prerequisites

- You have a Model Set with 3D models
- You have Model Coordination permissions
- Models are loaded and up to date

## 🚀 Steps to Create a Clash Test

### 1. Access Model Coordination

1. Go to https://acc.autodesk.com
2. Select your project
3. Click on **"Model Coordination"** in the sidebar menu
4. Open your **Model Set** (the one with ID: fd0473c1-3c46-4bd4-a30b-9987d1fb86c5)

### 2. Create a New Clash Test

1. In your Model Set, click on the **"Clash Tests"** tab (or "Tests de collision")
2. Click on **"New Clash Test"** or **"+ Create Test"**
3. Give the test a name (e.g.: "Structure vs MEP")

### 3. Configure Set A (First group of elements)

1. **"Set A"** section
2. Click on **"Add Selection"**
3. **Select a model**:
   - If you have a Structure model, select it
   - OR use a filter by discipline (Structure)
4. Optional: Add category filters
   - Example: Beams, Columns, Slabs
5. Validate the selection

### 4. Configure Set B (Second group of elements)

1. **"Set B"** section
2. Click on **"Add Selection"**
3. **Select another model**:
   - If you have an MEP model, select it
   - OR use a filter by discipline (MEP)
4. Optional: Add category filters
   - Example: Ducts, Pipes, Equipment
5. Validate the selection

### 5. Test Parameters

In the **"Test Settings"** section:

- **Tolerance**: Minimum distance (e.g.: 10mm or 0.01m)
- **Test Type**:
  - Hard Clash (physical collision)
  - Soft Clash (proximity)
- **Assign To**: Optional - assign to a team member

### 6. Run the Test

1. Click on **"Run Test"** or **"Lancer le test"**
2. ACC will analyze the models (may take a few minutes)
3. Results will appear in the interface

### 7. Verify in the API

Once the test is created and run:

1. Return to your Smart Clash Reporter application
2. Connect with Autodesk
3. Click on **"🔄 Load clashes from ACC"**
4. The clashes from the test should appear! 🎉

## 📊 Configuration Example

### Test: Structure vs Architecture

**Set A - Structure**
```
Model: Structure.rvt
Discipline: Structure
Categories: Beams, Columns, Slabs, Foundations
```

**Set B - Architecture**
```
Model: Architecture.rvt
Discipline: Architecture
Categories: Walls, Floors, Ceilings
```

**Parameters**
```
Tolerance: 5mm
Type: Hard Clash
```

### Test: MEP vs Structure

**Set A - MEP**
```
Model: MEP.rvt
Discipline: MEP
Categories: Ducts, Pipes, Equipment
```

**Set B - Structure**
```
Model: Structure.rvt
Discipline: Structure
Categories: Beams, Columns, Slabs
```

**Parameters**
```
Tolerance: 10mm
Type: Hard Clash
```

## 🎯 Important Points

### Difference between Views in ACC

What you see in the **"Clashes"** tab of the interface:
- These are **raw results** generated automatically
- They are **NOT accessible via the APS API** directly

What you create in the **"Clash Tests"** tab:
- These are **configured tests** with Set A vs Set B
- **ONLY these are accessible via the APS API**
- Once run, their results are accessible

### Clash Assignment

For the API to return clashes, they must be **assigned**:
1. After running a test, open its results
2. Select some clashes
3. Click on **"Assign"** (Assign)
4. Choose a team member
5. Validate

Assigned clashes will appear in the API!

## 🆘 Common Problems

### "I don't see the Clash Tests tab"

**Solution**:
- Check that you are in **Model Coordination**, not in "Docs"
- Check your permissions (Model Coordination Manager or Project Admin)

### "The test finds no clashes"

**Check**:
- Models in Set A and Set B are different
- Selected categories are correct
- Tolerance is not too low

### "The API still returns nothing after creating the test"

**Check**:
1. The test has been **run** (Run Test)
2. The test has completed execution
3. Clashes have been **assigned** to someone
4. Wait a few minutes (synchronization)
5. Refresh in the application

## ✅ Final Checklist

Before testing the API:

- [ ] I created a Clash Test in ACC Model Coordination
- [ ] I configured Set A with a model or discipline
- [ ] I configured Set B with another model or discipline
- [ ] I defined the tolerance and test type
- [ ] I ran the test (Run Test)
- [ ] The test finished and found clashes
- [ ] I assigned at least some clashes to a member
- [ ] I connected with OAuth 3-legged in the app
- [ ] I clicked on "🔄 Load clashes from ACC"

**Now clashes should appear in your application! 🎉**

## 📚 Resources

- [ACC Model Coordination Documentation](https://help.autodesk.com/view/ACCMOCO/ENU/)
- [APS Model Coordination API](https://aps.autodesk.com/en/docs/acc/v1/overview/field-guide/model-coordination/)
