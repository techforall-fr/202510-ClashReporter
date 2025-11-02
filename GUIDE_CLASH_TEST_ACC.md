# 🏗️ Guide: Configure a Clash Test in Autodesk ACC

## 📋 Prerequisites

Before configuring a clash test, ensure you have:
- ✅ An Autodesk ACC/BIM 360 account with project access
- ✅ Role with sufficient permissions (Project Admin or Model Coordination Manager)
- ✅ At least 2 3D models loaded in the project (Revit, Navisworks, etc.)
- ✅ Access to the **Model Coordination** module enabled

## 🚀 Steps to Create a Clash Test

### Step 1: Access Model Coordination

1. **Log in to Autodesk ACC**
   - Go to https://acc.autodesk.com
   - Select your project

2. **Open Model Coordination**
   - In the sidebar menu, click on **"Model Coordination"**
   - Or go directly to **"Coordination" > "Model Coordination"**

### Step 2: Create or Open a Model Set

A **Model Set** is a set of 3D models you want to coordinate.

1. **If you don't have a Model Set**:
   - Click on **"New Model Set"** (or "Nouveau jeu de modèles")
   - Give it a name (e.g.: "Project ABC - General Coordination")
   - Select the models to include
   - Click on **"Create"**

2. **If you already have a Model Set**:
   - Click on it to open it
   - This is the ID that should be in your `.env` → `APS_MODELSET_ID`

### Step 3: Create a Clash Test

1. **In your Opened Model Set**:
   - Click on the **"Clash Tests"** tab (or "Tests de collision")
   - Click on **"New Clash Test"** (or "Nouveau test")

2. **Clash Test Configuration**:

   **a) Test Name**
   - Give a descriptive name (e.g.: "Structure vs MEP")

   **b) Selection Set A (First group)**
   - Click on **"Add Selection"**
   - Choose the model (e.g.: Structure Model)
   - Optional: Filter by category (e.g.: Beams, Columns)
   - Optional: Define a discipline (Structure)

   **c) Selection Set B (Second group)**
   - Click on **"Add Selection"**
   - Choose the model (e.g.: MEP Model)
   - Optional: Filter by category (e.g.: Ducts, Pipes)
   - Optional: Define a discipline (MEP)

   **d) Test Parameters**
   - **Tolerance**: Minimum distance to consider a collision (e.g.: 10mm)
   - **Test Type**:
     - *Hard Clash*: Real physical collisions
     - *Soft Clash*: Proximity/clearance zone
   - **Clash Type**:
     - *New*: New collisions only
     - *Active*: Active collisions
     - *All*: All collisions

3. **Click on "Run Test"** (or "Lancer le test")
   - ACC will analyze the models
   - This may take a few minutes depending on size

### Step 4: Examine the Results

Once the test is completed:

1. **Clash View**
   - You will see the list of detected collisions
   - Each clash is classified by severity and status

2. **Details of a Clash**
   - Click on a clash to see:
     - Elements in collision (A and B)
     - 3D position
     - Collision distance
     - Comments and assignments

3. **Clash Management**
   - **Assign**: Assign to a team member
   - **Approve**: Approve (acceptable collision)
   - **Resolve**: Mark as resolved
   - **Comment**: Add comments

### Step 5: Obtain IDs for the Application

For your Smart Clash Reporter application to access the data:

1. **Obtaining the Model Set ID**
   - In your Model Set URL, you will see something like:
     ```
     https://acc.autodesk.com/...modelsets/fd0473c1-3c46-4bd4-a30b-9987d1fb86c5/...
     ```
   - The ID is: `fd0473c1-3c46-4bd4-a30b-9987d1fb86c5`
   - Copy it to your `.env`:
     ```env
     APS_MODELSET_ID=fd0473c1-3c46-4bd4-a30b-9987d1fb86c5
     ```

2. **Obtaining the Project ID**
   - Similarly, in the project URL:
     ```
     https://acc.autodesk.com/projects/5d2241e0-f646-4d83-975e-208a875bb138/...
     ```
   - The ID is: `5d2241e0-f646-4d83-975e-208a875bb138`
   - In your `.env`:
     ```env
     APS_PROJECT_ID=5d2241e0-f646-4d83-975e-208a875bb138
     ```

## 🎯 Typical Configuration Example

### Clash Test: Structure vs Architecture

**Set A - Structure**
- Model: `Structure.rvt`
- Categories: Beams, Columns, Slabs, Foundations
- Discipline: Structure

**Set B - Architecture**
- Model: `Architecture.rvt`
- Categories: Walls, Floors, Ceilings, Doors, Windows
- Discipline: Architecture

**Parameters**
- Tolerance: 5mm
- Type: Hard Clash
- Mode: Active

### Clash Test: MEP vs Structure

**Set A - MEP**
- Model: `MEP.rvt`
- Categories: Ducts, Pipes, Equipment
- Discipline: MEP

**Set B - Structure**
- Model: `Structure.rvt`
- Categories: Beams, Columns, Slabs
- Discipline: Structure

**Parameters**
- Tolerance: 10mm
- Type: Hard Clash
- Mode: Active

## 🔧 Best Practices

### 1. Test Organization
- Create specific tests per discipline
- Name your tests clearly (e.g.: "STR-vs-MEP", "ARCH-vs-STR")
- Document the tolerance used

### 2. Update Frequency
- Run tests after each model update
- Review clashes regularly (weekly recommended)
- Assign responsibilities quickly

### 3. Lifecycle Management
- **New** → New clash detected
- **Assigned** → Assigned to someone
- **In Review** → Under analysis
- **Resolved** → Resolved in the model
- **Approved** → Accepted (not critical)

### 4. Useful Filters
- By severity (High/Medium/Low)
- By status (Open/Resolved/Approved)
- By assignee
- By level/floor
- By discipline

## 📊 Understanding Results

### Clash Types

**Hard Clash**
- Elements that physically overlap
- ❌ **Critical**: Must be corrected immediately
- Example: A beam that goes through a duct

**Soft Clash**
- Elements too close (< tolerance)
- ⚠️ **Caution**: To be checked
- Example: Duct 5cm from a beam (tolerance = 10cm)

**Clearance Clash**
- Insufficient maintenance space
- ⚠️ **To plan**: Access required
- Example: Valve without space for maintenance

### Severity

The system automatically calculates severity based on:
- Intersection volume
- Element types
- System importance

## 🆘 Common Problems

### "No clashes detected" when there should be some

**Solutions**:
1. Verify that models are loaded and up to date
2. Check selection filters (Set A and Set B)
3. Increase tolerance if necessary
4. Ensure the test is run (Run Test)

### "Too many clashes" (thousands)

**Solutions**:
1. Refine selections (specific categories)
2. Reduce tolerance
3. Create several more targeted tests
4. Use filters by level/area

### "Cannot access via API"

**Verify**:
1. Your account has Model Coordination permissions
2. The Model Set exists and is active
3. IDs in `.env` are correct
4. 3-legged authentication is active

## 📚 Resources

- [Autodesk ACC Model Coordination Documentation](https://help.autodesk.com/view/ACCMOCO/ENU/)
- [APS Model Coordination API](https://aps.autodesk.com/en/docs/acc/v1/overview/field-guide/model-coordination/)
- [Autodesk Video Tutorial](https://www.youtube.com/results?search_query=autodesk+acc+model+coordination)

## ✅ Final Checklist

Before using the Smart Clash Reporter application:

- [ ] I created a Model Set with my 3D models
- [ ] I created at least one Clash Test
- [ ] I ran the test and obtained results
- [ ] I copied the Model Set ID to `.env`
- [ ] I copied the Project ID to `.env`
- [ ] My account has access to the ACC project
- [ ] I authenticated via 3-legged OAuth
- [ ] I clicked on "🔄 Load clashes from ACC"

**You are ready to use Smart Clash Reporter! 🎉**
