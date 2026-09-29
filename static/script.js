let currentReport = null;

function login() {
  const id = document.getElementById('farmerId').value.trim();
  const pass = document.getElementById('password').value;
  const error = document.getElementById('error');

  if (id === 'FARM001' && pass === '1234') {
    document.getElementById('loginPage').classList.add('hidden');
    document.getElementById('dashboardPage').classList.remove('hidden');
    document.getElementById('loggedUser').textContent = id;
    error.textContent = '';
  } else {
    error.textContent = 'Invalid credentials. Use FARM001 / 1234 for the demo.';
  }
}

function logout() {
  document.getElementById('dashboardPage').classList.add('hidden');
  document.getElementById('loginPage').classList.remove('hidden');
  document.getElementById('password').value = '';
}

async function generateRecommendation() {
  const data = {
    soil: document.getElementById('soil').value,
    season: document.getElementById('season').value,
    temp: document.getElementById('temp').value,
    humidity: document.getElementById('humidity').value,
    rain: document.getElementById('rain').value,
    moisture: document.getElementById('moisture').value,
    n: document.getElementById('n').value,
    p: document.getElementById('p').value,
    k: document.getElementById('k').value,
  };

  const response = await fetch('/api/recommend', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  const result = await response.json();

  if (!result.success) {
    alert(result.message || 'Something went wrong');
    return;
  }

  currentReport = { ...data, ...result };

  document.getElementById('crop').textContent = result.crop;
  document.getElementById('fert').textContent = result.fertilizer;
  document.getElementById('yield').textContent = result.yield;
  document.getElementById('water').textContent = result.water;

  const score = result.score;
  document.getElementById('scorebar').style.width = score + '%';
  document.getElementById('score').textContent = score + '% suitable conditions';

  document.getElementById('explain').innerHTML = result.message;
}

async function downloadReport() {
  if (!currentReport) {
    alert('Please generate a recommendation before downloading.');
    return;
  }

  const response = await fetch('/api/report', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(currentReport)
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'agriculture_report.csv';
  document.body.appendChild(a);
  a.click();
  a.remove();
}
