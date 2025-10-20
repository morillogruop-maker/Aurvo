<!DOCTYPE html><html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AURVO OS Roadmap — Oro en Movimiento</title>
  <style>
    body {
      font-family: 'Orbitron', sans-serif;
      background: linear-gradient(135deg, #000000 60%, #1a1a1a);
      color: #d4af37;
      margin: 0;
      padding: 0;
      overflow-x: hidden;
    }
    header {
      text-align: center;
      padding: 30px 0;
      border-bottom: 2px solid #d4af37;
      box-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
    }
    h1 {
      font-size: 2.5em;
      text-shadow: 0 0 10px #d4af37;
    }
    .roadmap {
      display: flex;
      flex-wrap: nowrap;
      overflow-x: auto;
      scroll-behavior: smooth;
      padding: 40px;
      gap: 30px;
    }
    .phase {
      background: rgba(20, 20, 20, 0.95);
      border: 1px solid #d4af37;
      border-radius: 16px;
      box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
      min-width: 360px;
      flex: 0 0 auto;
      padding: 20px;
      transition: transform 0.3s;
    }
    .phase:hover {
      transform: translateY(-5px);
      box-shadow: 0 0 30px rgba(212, 175, 55, 0.5);
    }
    h2 {
      text-align: center;
      border-bottom: 1px solid #d4af37;
      padding-bottom: 10px;
      margin-bottom: 20px;
    }
    ul {
      list-style: none;
      padding-left: 0;
    }
    li {
      background: rgba(255, 215, 0, 0.1);
      border-left: 3px solid #d4af37;
      margin: 10px 0;
      padding: 10px;
      border-radius: 8px;
    }
    footer {
      text-align: center;
      padding: 20px;
      border-top: 1px solid