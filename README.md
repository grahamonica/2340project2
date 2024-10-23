# Food Finder

## Setup Django app

1. Create a conda environment:
   ```
   conda create -n food_finder python==3.10.12
   ```

2. Activate the environment:
   ```
   conda activate food_finder
   ```

3. Install dependencies:
   ```
   pip install -U charset_normalizer # in case google maps gives an error later
   pip install -r requirements.txt
   ```

## Setup Next.js frontend

Install dependencies (if first time using):
```
cd frontend
npm install
```

Start the development server:
```
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You also need to start the Django server so the frontend can communicate with it. First set the environment variable with the google maps API key to enable search, etc.

Add this line to a file called `.env` in the root directory:

GOOGLE_MAPS_API_KEY="<api-key-value>"

Now in a separate terminal window, start the Django server:

```
cd .. # into root directory
python manage.py runserver
```

You'll have two terminal windows running the Django server and the Next.js development server respectively.