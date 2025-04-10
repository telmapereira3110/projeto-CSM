import { useEffect, useState } from "react";
import {Bar} from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [tipoAnalise, setTipoAnalise] = useState("");
  const [jogador, setJogador] = useState(""); // Estado para armazenar o jogador selecionado
  const [jogador1, setJogador1] = useState(""); 
  const [jogador2, setJogador2] = useState(""); 
  const [jogadores, setJogadores] = useState([]); // Lista de Jogadores
  const [microciclo, setMicrociclo] = useState(1); // Estado para armazenar o microciclo selecionado
  const [microciclos, setMicrociclos] = useState([]);
  const [wellness, setWellness] = useState(null); // Dados do questionário do jogador
  const [wellnessJogador1, setWellnessJogador1] = useState(null);
  const [wellnessJogador2, setWellnessJogador2] = useState(null);
  const [variavel, setVariavel] = useState("Wellness"); // Estado para armazenar a análise selecionada
  const [pseData, setPseData] = useState([]); // Dados da PSE do jogador
  const [pseDataJogador1, setPseDataJogador1] = useState([]); // Dados da PSE do jogador
  const [pseDataJogador2, setPseDataJogador2] = useState([]); // Dados da PSE do jogador
  const [cargaInternaData, setCargaInternaData] = useState([]);
  const [cargaInternaDataJogador1, setCargaInternaDataJogador1] = useState([]);
  const [cargaInternaDataJogador2, setCargaInternaDataJogador2] = useState([]);
  const [racioData, setRacioData] = useState(null);
  const [racioDataJogador1, setRacioDataJogador1] = useState(null);
  const [racioDataJogador2, setRacioDataJogador2] = useState(null);
  const [cargaExternaDtData, setCargaExternaDtData] = useState([]);
  const [cargaExternaDtDataJogador1, setCargaExternaDtDataJogador1] = useState([]);
  const [cargaExternaDtDataJogador2, setCargaExternaDtDataJogador2] = useState([]);
  const [racioDtData, setRacioDtData] = useState(null);
  const [racioDtDataJogador1, setRacioDtDataJogador1] = useState(null);
  const [racioDtDataJogador2, setRacioDtDataJogador2] = useState(null);
  const [mDtData, setMDtData] = useState(null);
  const [cargaExternaHsData, setCargaExternaHsData] = useState([]);
  const [cargaExternaHsDataJogador1, setCargaExternaHsDataJogador1] = useState([]);
  const [cargaExternaHsDataJogador2, setCargaExternaHsDataJogador2] = useState([]);
  const [racioHsData, setRacioHsData] = useState(null);
  const [racioHsDataJogador1, setRacioHsDataJogador1] = useState(null);
  const [racioHsDataJogador2, setRacioHsDataJogador2] = useState(null);
  const [mHsData, setMHsData] = useState(null);
  const [monotoniaData, setMonotoniaData] = useState(null);
  const [strainData, setStrainData] = useState(null);
  const [zScorePSE, setZScorePSE] = useState(null);
  const [zScoreDT, setZScoreDT] = useState(null);
  const [zScoreWellness, setZScoreWellness] = useState(null);
  const [zScoreMonotonia, setZScoreMonotonia] = useState(null);
  const [zScoreStrain, setZScoreStrain] = useState(null);
  const [cmjData, setCMJData] = useState(null);
  const [sjData, setSJData] = useState(null);



  // Buscar os jogadores da API Flask quando a página carregar
  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/jogadores") // Chama o Flask
      .then((response) => response.json())
      .then((data) => setJogadores(data)) // Atualiza a lista de jogadores
      .catch((error) => console.error("Erro ao buscar jogadores:", error));

    fetch("http://127.0.0.1:5000/api/microciclos") // Chama o Flask
      .then((response) => response.json())
      .then((data) => setMicrociclos(data)) // Atualiza a lista de jogadores
      .catch((error) => console.error("Erro ao buscar microciclos:", error));
  }, []);

  // Buscar os dados do questionário para o jogador e microciclo selecionado (Análise Individual)
  useEffect(() => {
    if (jogador && microciclo) {
      fetch(`http://127.0.0.1:5000/api/wellness/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setWellness(data)) // Atualiza os dados do microciclo
        .catch((error) => console.error("Erro ao buscar questionário:", error));

      fetch(`http://127.0.0.1:5000/api/pse/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setPseData(data))
        .catch((error) => console.error("Erro ao buscar PSE:", error));

      fetch(`http://127.0.0.1:5000/api/carga_interna/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCargaInternaData(data))
        .catch((error) => console.error("Erro ao buscar Carga Interna:", error));

      fetch(`http://127.0.0.1:5000/api/carga_externa_dt/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCargaExternaDtData(data))
        .catch((error) => console.error("Erro ao buscar Carga Externa da Distância Total:", error));

      fetch(`http://127.0.0.1:5000/api/carga_externa_hs/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCargaExternaHsData(data))
        .catch((error) => console.error("Erro ao buscar Carga Externa da Distância em Alta Velocidade:", error));

      fetch(`http://127.0.0.1:5000/api/zscore/acwr_pse/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setZScorePSE(data)) 
        .catch((error) => console.error("Erro ao buscar Z-score ACWR PSE:", error));
  
      fetch(`http://127.0.0.1:5000/api/zscore/acwr_dt/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setZScoreDT(data))
        .catch((error) => console.error("Erro ao buscar Z-score ACWR DT:", error));
  
      fetch(`http://127.0.0.1:5000/api/zscore/wellness/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setZScoreWellness(data))
        .catch((error) => console.error("Erro ao buscar Z-score Wellness:", error));
  
      fetch(`http://127.0.0.1:5000/api/zscore/monotonia/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setZScoreMonotonia(data))
        .catch((error) => console.error("Erro ao buscar Z-score Monotonia:", error));
  
      fetch(`http://127.0.0.1:5000/api/zscore/strain/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setZScoreStrain(data))
        .catch((error) => console.error("Erro ao buscar Z-score Strain:", error));

      fetch(`http://127.0.0.1:5000/api/cmj/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCMJData(data))
        .catch((error) => console.error("Erro ao buscar CMJ:", error));

      fetch(`http://127.0.0.1:5000/api/sj/${jogador}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setSJData(data))
        .catch((error) => console.error("Erro ao buscar SJ:", error));
    }
  }, [jogador, microciclo]); // Executa sempre que o jogador ou microciclo mudar

  useEffect(()=> {
    if (jogador) {
      fetch(`http://127.0.0.1:5000/api/racio/${jogador}`)
        .then((response) => response.json())
        .then((data) => setRacioData(data))
        .catch((error) => console.error("Erro ao buscar Racio da Carga Interna:", error));

      fetch(`http://127.0.0.1:5000/api/racio_dt/${jogador}`)
        .then((response) => response.json())
        .then((data) => setRacioDtData(data))
        .catch((error) => console.error("Erro ao buscar Racio da Carga Externa da Distância Total:", error));
      
      fetch(`http://127.0.0.1:5000/api/racio_hs/${jogador}`)
        .then((response) => response.json())
        .then((data) => setRacioHsData(data))
        .catch((error) => console.error("Erro ao buscar Racio da Carga Externa da Distância em Alta Velocidade:", error));

      fetch(`http://127.0.0.1:5000/api/m_dt/${jogador}`)
        .then((response) => response.json())
        .then((data) => setMDtData(data))
        .catch((error) => console.error("Erro ao buscar M% da Carga Externa da Distância Total:", error));

      fetch(`http://127.0.0.1:5000/api/m_hs/${jogador}`)
        .then((response) => response.json())
        .then((data) => setMHsData(data))
        .catch((error) => console.error("Erro ao buscar M% da Carga Externa da Distância em Alta Velocidade:", error));

      fetch(`http://127.0.0.1:5000/api/monotonia/${jogador}`)
        .then((response) => response.json())
        .then((data) => setMonotoniaData(data))
        .catch((error) => console.error("Erro ao buscar Monotonia:", error));
      
      fetch(`http://127.0.0.1:5000/api/strain/${jogador}`)
        .then((response) => response.json())
        .then((data) => setStrainData(data))
        .catch((error) => console.error("Erro ao buscar Strain:", error));
    }
  }, [jogador]);

  // Buscar os dados do questionário para o jogador 1 e microciclo selecionado (Análise Comparativa)
  useEffect(() => {
    if (jogador1 && microciclo) {
      fetch(`http://127.0.0.1:5000/api/wellness/${jogador1}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setWellnessJogador1(data)) // Atualiza os dados do microciclo
        .catch((error) => console.error("Erro ao buscar questionário:", error));

      fetch(`http://127.0.0.1:5000/api/pse/${jogador1}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setPseDataJogador1(data))
        .catch((error) => console.error("Erro ao buscar PSE:", error));

      fetch(`http://127.0.0.1:5000/api/carga_interna/${jogador1}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCargaInternaDataJogador1(data))
        .catch((error) => console.error("Erro ao buscar Carga Interna:", error));

      fetch(`http://127.0.0.1:5000/api/carga_externa_dt/${jogador1}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCargaExternaDtDataJogador1(data))
        .catch((error) => console.error("Erro ao buscar Carga Externa da Distância Total:", error));

      fetch(`http://127.0.0.1:5000/api/carga_externa_hs/${jogador1}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCargaExternaHsDataJogador1(data))
        .catch((error) => console.error("Erro ao buscar Carga Externa da Distância em Alta Velocidade:", error));      
    }
  }, [jogador1, microciclo]); // Executa sempre que o jogador ou microciclo mudar

  useEffect(()=> {
    if (jogador1) {
      fetch(`http://127.0.0.1:5000/api/racio/${jogador1}`)
        .then((response) => response.json())
        .then((data) => setRacioDataJogador1(data))
        .catch((error) => console.error("Erro ao buscar Racio da Carga Interna:", error));

      fetch(`http://127.0.0.1:5000/api/racio_dt/${jogador1}`)
        .then((response) => response.json())
        .then((data) => setRacioDtDataJogador1(data))
        .catch((error) => console.error("Erro ao buscar Racio da Carga Externa da Distância Total:", error));
      
      fetch(`http://127.0.0.1:5000/api/racio_hs/${jogador1}`)
        .then((response) => response.json())
        .then((data) => setRacioHsDataJogador1(data))
        .catch((error) => console.error("Erro ao buscar Racio da Carga Externa da Distância em Alta Velocidade:", error));

      fetch(`http://127.0.0.1:5000/api/monotonia/${jogador1}`)
        .then((response) => response.json())
        .then((data) => setMonotoniaData(data))
        .catch((error) => console.error("Erro ao buscar Monotonia:", error));
      
      fetch(`http://127.0.0.1:5000/api/strain/${jogador1}`)
        .then((response) => response.json())
        .then((data) => setStrainData(data))
        .catch((error) => console.error("Erro ao buscar Strain:", error));
    }
  }, [jogador1]);

  // Buscar os dados do questionário para o jogador 2 e microciclo selecionado (Análise Comparativa)
  useEffect(() => {
    if (jogador2 && microciclo) {
      fetch(`http://127.0.0.1:5000/api/wellness/${jogador2}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setWellnessJogador2(data)) // Atualiza os dados do microciclo
        .catch((error) => console.error("Erro ao buscar questionário:", error));

      fetch(`http://127.0.0.1:5000/api/pse/${jogador2}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setPseDataJogador2(data))
        .catch((error) => console.error("Erro ao buscar PSE:", error));

      fetch(`http://127.0.0.1:5000/api/carga_interna/${jogador2}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCargaInternaDataJogador2(data))
        .catch((error) => console.error("Erro ao buscar Carga Interna:", error));

      fetch(`http://127.0.0.1:5000/api/carga_externa_dt/${jogador2}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCargaExternaDtDataJogador2(data))
        .catch((error) => console.error("Erro ao buscar Carga Externa da Distância Total:", error));

      fetch(`http://127.0.0.1:5000/api/carga_externa_hs/${jogador2}/${microciclo}`)
        .then((response) => response.json())
        .then((data) => setCargaExternaHsDataJogador2(data))
        .catch((error) => console.error("Erro ao buscar Carga Externa da Distância em Alta Velocidade:", error));      
    }
  }, [jogador2, microciclo]); // Executa sempre que o jogador ou microciclo mudar

  useEffect(()=> {
    if (jogador2) {
      fetch(`http://127.0.0.1:5000/api/racio/${jogador2}`)
        .then((response) => response.json())
        .then((data) => setRacioDataJogador2(data))
        .catch((error) => console.error("Erro ao buscar Racio da Carga Interna:", error));

      fetch(`http://127.0.0.1:5000/api/racio_dt/${jogador2}`)
        .then((response) => response.json())
        .then((data) => setRacioDtDataJogador2(data))
        .catch((error) => console.error("Erro ao buscar Racio da Carga Externa da Distância Total:", error));
      
      fetch(`http://127.0.0.1:5000/api/racio_hs/${jogador2}`)
        .then((response) => response.json())
        .then((data) => setRacioHsDataJogador2(data))
        .catch((error) => console.error("Erro ao buscar Racio da Carga Externa da Distância em Alta Velocidade:", error));      

      fetch(`http://127.0.0.1:5000/api/monotonia/${jogador2}`)
        .then((response) => response.json())
        .then((data) => setMonotoniaData(data))
        .catch((error) => console.error("Erro ao buscar Monotonia:", error));
      
      fetch(`http://127.0.0.1:5000/api/strain/${jogador2}`)
        .then((response) => response.json())
        .then((data) => setStrainData(data))
        .catch((error) => console.error("Erro ao buscar Strain:", error));
    }
  }, [jogador2]);

  // Ordem correta dos dias da semana
  const ordemDias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"];

  // Tamanho e título para os gráficos
  const tamanho = {
    maintainAspectRatio: false, // Permite ajustar a proporção
    responsive: true, // Faz o gráfico se adaptar ao contêiner
    plugins: {
      title: {
        display: true, // Exibe o título
        text: '', // Título vazio, que será configurado dinamicamente
        font: {
          size: 18,
        },
      },
    },
  };

  // Função para obter o intervalo de datas do microciclo para o Wellness
  const obterIntervaloDatas = () => {
    if (!wellness) return "";

    // Pega as chaves dos dias dentro do microciclo
    const dias = Object.keys(wellness);

    if (dias.length === 0) return ""; // Caso não haja dias no microciclo

    // Ordenar as datas para garantir que elas estão na ordem cronológica
    const datas = dias
      .map(dia => wellness[dia]?.data)  // Pega as datas associadas a cada dia
      .filter(Boolean) // Remove valores undefined ou nulos
      .sort(); // Ordena as datas em ordem crescente

    if (datas.length === 0) return ""; // Caso não haja datas válidas

    const dataInicio = datas[0]; // Primeira data (início do microciclo)
    const dataFim = datas[datas.length - 1]; // Última data (fim do microciclo)

    // Formata as datas para o formato desejado
    return `de ${formatarData(dataInicio)} até ${formatarData(dataFim)}`;
  };

  // Função para formatar a data no formato dd/mm/aaaa
  const formatarData = (data) => {
    const [ano, mes, dia] = data.split('-');
    return `${dia}/${mes}/${ano}`;
  };


  // Função para obter o intervalo de datas do microciclo para a PSE e Carga de Treino
  const obterIntervaloDatasPse = () => {
    if (!pseData || Object.keys(pseData).length === 0) return "";

    let datas = [];

    // Itera pelos dias do microciclo e coleta todas as datas de treino
    Object.values(pseData).forEach((treinos) => {
      treinos.forEach((treino) => {
        if (treino.data_treino) {
          datas.push(treino.data_treino);
        }
      });
    });

    if (datas.length === 0) return ""; // Se não houver dados

    // Ordenar datas corretamente
  datas = [...new Set(datas)].sort(); // Remove duplicatas e ordena

  const dataInicio = datas[0]; // Primeira data
  const dataFim = datas[datas.length - 1]; // Última data

    // Formata as datas para o formato desejado
    return `de ${formatarDataPse(dataInicio)} até ${formatarDataPse(dataFim)}`;
  };

  // Função para formatar a data no formato dd/mm/aaaa
  const formatarDataPse = (data) => {
    const [ano, mes, dia] = data.split('-');
    return `${dia}/${mes}/${ano}`;
  };

  
  // Função para calcular a média de uma variável para o Wellness
  const calcularMediaWellness = (variavel) => {
    if (!wellness) return 0;

    const soma = ordemDias.reduce((acc, dia) => acc + (wellness[dia]?.[variavel] || 0), 0);
    return soma / ordemDias.length;
  };

  // Calcular médias para cada variável
  const mediaSono = calcularMediaWellness('sono');
  const mediaFadiga = calcularMediaWellness('fadiga');
  const mediaDorMuscular = calcularMediaWellness('dor_muscular');
  const mediaStress = calcularMediaWellness('stress');

  // Função para calcular a média de uma variável para o Wellness
  const calcularMediaWellnessJogador1 = (variavel) => {
    if (!wellnessJogador1) return 0;

    const soma = ordemDias.reduce((acc, dia) => acc + (wellnessJogador1[dia]?.[variavel] || 0), 0);
    return soma / ordemDias.length;
  };

  // Calcular médias para cada variável
  const mediaSonoJogador1 = calcularMediaWellnessJogador1('sono');
  const mediaFadigaJogador1 = calcularMediaWellnessJogador1('fadiga');
  const mediaDorMuscularJogador1 = calcularMediaWellnessJogador1('dor_muscular');
  const mediaStressJogador1 = calcularMediaWellnessJogador1('stress');

  // Função para calcular a média de uma variável para o Wellness
  const calcularMediaWellnessJogador2 = (variavel) => {
    if (!wellnessJogador2) return 0;

    const soma = ordemDias.reduce((acc, dia) => acc + (wellnessJogador2[dia]?.[variavel] || 0), 0);
    return soma / ordemDias.length;
  };

  // Calcular médias para cada variável
  const mediaSonoJogador2 = calcularMediaWellnessJogador2('sono');
  const mediaFadigaJogador2 = calcularMediaWellnessJogador2('fadiga');
  const mediaDorMuscularJogador2 = calcularMediaWellnessJogador2('dor_muscular');
  const mediaStressJogador2 = calcularMediaWellnessJogador2('stress');


  const dataWellness = {
    labels: ordemDias,
    datasets: [
      {
        label: "Sono",
        data: ordemDias.map(dia => wellness?.[dia]?.sono || 0),
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        borderColor: "rgb(75, 192, 192)",
        borderWidth: 1,
      },
      {
        label: "Fadiga",
        data: ordemDias.map(dia => wellness?.[dia]?.fadiga || 0),
        backgroundColor: "rgba(255, 99, 132, 0.5)",
        borderColor: "rgb(255, 99, 132)",
        borderWidth: 1,
      },
      {
        label: "Dor Muscular",
        data: ordemDias.map(dia => wellness?.[dia]?.dor_muscular || 0),
        backgroundColor: "rgba(255, 206, 86, 0.5)",
        borderColor: "rgb(255, 206, 86)",
        borderWidth: 1,
      },
      {
        label: "Stress",
        data: ordemDias.map(dia => wellness?.[dia]?.stress || 0),
        backgroundColor: "rgba(105, 235, 54, 0.5)",
        borderColor: "rgb(114, 235, 54)",
        borderWidth: 1,
      },
    ],
  };

  // Dados para o gráfico das médias do Wellness
  const dataMedias =  {
    labels: ['Sono', 'Fadiga', 'Dor Muscular', 'Stress'],
    datasets: [
      {
        label: 'Média',
        data: [mediaSono, mediaFadiga, mediaDorMuscular, mediaStress],
        backgroundColor: [
          "rgba(75, 192, 192, 0.5)",
          "rgba(75, 192, 192, 0.5)",
          "rgba(75, 192, 192, 0.5)",
          "rgba(75, 192, 192, 0.5)",
        ],
        borderColor: [
          "rgb(75, 192, 192)",
          "rgb(75, 192, 192)",
          "rgb(75, 192, 192)",
          "rgb(75, 192, 192)",
        ],
        borderWidth: 1,
      },
    ],
  };

  // Dados para o gráfico das médias do Wellness
  const dataMediasJogador1 =  {
    labels: ['Sono', 'Fadiga', 'Dor Muscular', 'Stress'],
    datasets: [
      {
        label: 'Média',
        data: [mediaSonoJogador1, mediaFadigaJogador1, mediaDorMuscularJogador1, mediaStressJogador1],
        backgroundColor: [
          "rgba(75, 192, 192, 0.5)",
          "rgba(75, 192, 192, 0.5)",
          "rgba(75, 192, 192, 0.5)",
          "rgba(75, 192, 192, 0.5)",
        ],
        borderColor: [
          "rgb(75, 192, 192)",
          "rgb(75, 192, 192)",
          "rgb(75, 192, 192)",
          "rgb(75, 192, 192)",
        ],
        borderWidth: 1,
      },
    ],
  };

  // Dados para o gráfico das médias do Wellness
  const dataMediasJogador2 =  {
    labels: ['Sono', 'Fadiga', 'Dor Muscular', 'Stress'],
    datasets: [
      {
        label: 'Média',
        data: [mediaSonoJogador2, mediaFadigaJogador2, mediaDorMuscularJogador2, mediaStressJogador2],
        backgroundColor: [
          "rgba(75, 192, 192, 0.5)",
          "rgba(75, 192, 192, 0.5)",
          "rgba(75, 192, 192, 0.5)",
          "rgba(75, 192, 192, 0.5)",
        ],
        borderColor: [
          "rgb(75, 192, 192)",
          "rgb(75, 192, 192)",
          "rgb(75, 192, 192)",
          "rgb(75, 192, 192)",
        ],
        borderWidth: 1,
      },
    ],
  };

  // Função para verificar se um valor precisa de alerta Wellness
  const verificarAlertaWellness = (valor) => {
    return valor >= 6 ? { color: "orange", fontWeight: "bold" } : {};
  };

  // Processamento de dados para o gráfico PSE
  const labels = [];
  const dadosPSE = [];

  // Iterar pelos dias da semana, garantindo ordem correta
  ordemDias.forEach((dia) => {
    if (pseData[dia]) {
      pseData[dia].forEach((treino) => {
        labels.push(treino.data_treino);
        dadosPSE.push(parseFloat(treino.pse) || 0);
      });
    } else {
      labels.push(dia);
      dadosPSE.push(0); // Caso não haja treino nesse dia
    }
  });

  const dataPSE = {
    labels: labels,
    datasets: [
      {
        label: "PSE",
        data: dadosPSE,
        backgroundColor: "rgba(54, 162, 235, 0.5)",
      },
    ],
  };

  // Processamento de dados para o gráfico PSE
  const labelsJogador1 = [];
  const dadosPSEJogador1 = [];

  // Iterar pelos dias da semana, garantindo ordem correta
  ordemDias.forEach((dia) => {
    if (pseDataJogador1[dia]) {
      pseDataJogador1[dia].forEach((treino) => {
        labelsJogador1.push(treino.data_treino);
        dadosPSEJogador1.push(parseFloat(treino.pse) || 0);
      });
    } else {
      labelsJogador1.push(dia);
      dadosPSEJogador1.push(0); // Caso não haja treino nesse dia
    }
  });

  const dataPSEJogador1 = {
    labels: labelsJogador1,
    datasets: [
      {
        label: "PSE",
        data: dadosPSEJogador1,
        backgroundColor: "rgba(54, 162, 235, 0.5)",
      },
    ],
  };

  // Processamento de dados para o gráfico PSE
  const labelsJogador2 = [];
  const dadosPSEJogador2 = [];

  // Iterar pelos dias da semana, garantindo ordem correta
  ordemDias.forEach((dia) => {
    if (pseDataJogador2[dia]) {
      pseDataJogador2[dia].forEach((treino) => {
        labelsJogador2.push(treino.data_treino);
        dadosPSEJogador2.push(parseFloat(treino.pse) || 0);
      });
    } else {
      labelsJogador2.push(dia);
      dadosPSEJogador2.push(0); // Caso não haja treino nesse dia
    }
  });

  const dataPSEJogador2 = {
    labels: labelsJogador2,
    datasets: [
      {
        label: "PSE",
        data: dadosPSEJogador2,
        backgroundColor: "rgba(54, 162, 235, 0.5)",
      },
    ],
  };

  // Função para verificar se um valor precisa de alerta PSE
  const verificarAlertaPSE = (valor) => {
    return valor >= 9 ? { color: "orange", fontWeight: "bold" } : {};
  };

  // Processamento de dados para o gráfico Carga Interna
  const labelsCargaInterna = [];
  const dadosCargaInterna = [];

  // Iterar pelos dias da semana, garantindo ordem correta
  ordemDias.forEach((dia) => {
    if (cargaInternaData[dia]) {
      cargaInternaData[dia].forEach((treino) => {
        labelsCargaInterna.push(treino.data_treino);
        dadosCargaInterna.push(treino.carga_interna || 0);
      });
    } else {
      labelsCargaInterna.push(dia);
      dadosCargaInterna.push(0); // Caso não haja treino nesse dia
    }
  });

  const dataCargaInterna = {
    labels: labelsCargaInterna,
    datasets: [
      {
        label: "Carga da Sessão",
        data: dadosCargaInterna,
        backgroundColor: "rgba(54, 162, 235, 0.5)",
      },
    ],
  };

   // Processamento de dados para o gráfico da Carga Interna do Jogador 1
  const labelsCargaInternaJogador1 = [];
  const dadosCargaInternaJogador1 = [];

  // Iterar pelos dias da semana, garantindo ordem correta
  ordemDias.forEach((dia) => {
    if (cargaInternaDataJogador1[dia]) {
      cargaInternaDataJogador1[dia].forEach((treino) => {
        labelsCargaInternaJogador1.push(treino.data_treino);
        dadosCargaInternaJogador1.push(treino.carga_interna || 0);
      });
    } else {
      labelsCargaInternaJogador1.push(dia);
      dadosCargaInternaJogador1.push(0); // Caso não haja treino nesse dia
    }
  });

  const dataCargaInternaJogador1 = {
    labels: labelsCargaInternaJogador1,
    datasets: [
      {
        label: "Carga da Sessão",
        data: dadosCargaInternaJogador1,
        backgroundColor: "rgba(54, 162, 235, 0.5)",
      },
    ],
  };


  // Dados para a Carga Interna do Jogador 2
  const labelsCargaInternaJogador2 = [];
  const dadosCargaInternaJogador2 = [];

  // Iterar pelos dias da semana, garantindo ordem correta
  ordemDias.forEach((dia) => {
    if (cargaInternaDataJogador2[dia]) {
      cargaInternaDataJogador2[dia].forEach((treino) => {
        labelsCargaInternaJogador2.push(treino.data_treino);
        dadosCargaInternaJogador2.push(treino.carga_interna || 0);
      });
    } else {
      labelsCargaInternaJogador2.push(dia);
      dadosCargaInternaJogador2.push(0); // Caso não haja treino nesse dia
    }
  });

  const dataCargaInternaJogador2 = {
    labels: labelsCargaInternaJogador2,
    datasets: [
      {
        label: "Carga da Sessão",
        data: dadosCargaInternaJogador2,
        backgroundColor: "rgba(54, 162, 235, 0.5)",
      },
    ],
  };


  // Acumular valores de ACWR da carga interna para os gráficos
  const gerarValoresACWR = () => {
    const acwrValores = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número

  
    // Acessar os dados do ACWR para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const acwrMicrociclo = racioData?.[i] || 0; // Pega o ACWR para cada microciclo
      acwrValores.push(acwrMicrociclo);
    }
  
    return acwrValores;
  };

  // Acumular valores de ACWR da carga interna do Jogador 1 para os gráficos
  const gerarValoresACWRJogador1 = () => {
    const acwrValoresJogador1 = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número

  
    // Acessar os dados do ACWR para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const acwrMicrocicloJogador1 = racioDataJogador1?.[i] || 0; // Pega o ACWR para cada microciclo
      acwrValoresJogador1.push(acwrMicrocicloJogador1);
    }
  
    return acwrValoresJogador1;
  };
  

  // Acumular valores de ACWR da carga interna do Jogador 2 para os gráficos
  const gerarValoresACWRJogador2 = () => {
    const acwrValoresJogador2 = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número

  
    // Acessar os dados do ACWR para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const acwrMicrocicloJogador2 = racioDataJogador2?.[i] || 0; // Pega o ACWR para cada microciclo
      acwrValoresJogador2.push(acwrMicrocicloJogador2);
    }
  
    return acwrValoresJogador2;
  };

  // Dados para a Carga Externa DT
  const labelsCargaExternaDT = [];
  const dadosCargaExternaDT = [];

  ordemDias.forEach((dia) => {
    if (cargaExternaDtData[dia]) {
      cargaExternaDtData[dia].forEach((treino) => {
        labelsCargaExternaDT.push(treino.data_treino);
        dadosCargaExternaDT.push(treino.distancia_total || 0);
      });
    } else {
      labelsCargaExternaDT.push(dia);
      dadosCargaExternaDT.push(0); 
    }
  });

  const dataCargaExternaDT = {
    labels: labelsCargaExternaDT,
    datasets: [
      {
        label: "Carga Externa DT",
        data: dadosCargaExternaDT,
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        borderColor: "rgb(75, 192, 192)",
        borderWidth: 1,
      },
    ],
  };

  // Dados para a Carga Externa DT do Jogador 1
  const labelsCargaExternaDTJogador1 = [];
  const dadosCargaExternaDTJogador1 = [];

  ordemDias.forEach((dia) => {
    if (cargaExternaDtDataJogador1[dia]) {
      cargaExternaDtDataJogador1[dia].forEach((treino) => {
        labelsCargaExternaDTJogador1.push(treino.data_treino);
        dadosCargaExternaDTJogador1.push(treino.distancia_total || 0);
      });
    } else {
      labelsCargaExternaDTJogador1.push(dia);
      dadosCargaExternaDTJogador1.push(0); 
    }
  });

  const dataCargaExternaDTJogador1 = {
    labels: labelsCargaExternaDTJogador1,
    datasets: [
      {
        label: "Carga Externa DT",
        data: dadosCargaExternaDTJogador1,
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        borderColor: "rgb(75, 192, 192)",
        borderWidth: 1,
      },
    ],
  };

  // Dados para a Carga Externa DT do Jogador 2
  const labelsCargaExternaDTJogador2 = [];
  const dadosCargaExternaDTJogador2 = [];

  ordemDias.forEach((dia) => {
    if (cargaExternaDtDataJogador2[dia]) {
      cargaExternaDtDataJogador2[dia].forEach((treino) => {
        labelsCargaExternaDTJogador2.push(treino.data_treino);
        dadosCargaExternaDTJogador2.push(treino.distancia_total || 0);
      });
    } else {
      labelsCargaExternaDTJogador2.push(dia);
      dadosCargaExternaDTJogador2.push(0); 
    }
  });

  const dataCargaExternaDTJogador2 = {
    labels: labelsCargaExternaDTJogador2,
    datasets: [
      {
        label: "Carga Externa DT",
        data: dadosCargaExternaDTJogador2,
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        borderColor: "rgb(75, 192, 192)",
        borderWidth: 1,
      },
    ],
  };

  // Acumular valores de ACWR da carga externa DT para os gráficos
  const gerarValoresACWRdt = () => {
    const acwrDtValores = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número

  
    // Acessar os dados do ACWR para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const acwrDtMicrociclo = racioDtData?.[i] || 0; // Pega o ACWR para cada microciclo
      acwrDtValores.push(acwrDtMicrociclo);
    }
  
    return acwrDtValores;
  };


  // Acumular valores de ACWR da carga externa DT do Jogador 1 para os gráficos
  const gerarValoresACWRdtJogador1 = () => {
    const acwrDtValoresJogador1 = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número

  
    // Acessar os dados do ACWR para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const acwrDtMicrocicloJogador1 = racioDtDataJogador1?.[i] || 0; // Pega o ACWR para cada microciclo
      acwrDtValoresJogador1.push(acwrDtMicrocicloJogador1);
    }
  
    return acwrDtValoresJogador1;
  };
  
  // Acumular valores de ACWR da carga externa DT do Jogador 2 para os gráficos
  const gerarValoresACWRdtJogador2 = () => {
    const acwrDtValoresJogador2 = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número

  
    // Acessar os dados do ACWR para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const acwrDtMicrocicloJogador2 = racioDtDataJogador2?.[i] || 0; // Pega o ACWR para cada microciclo
      acwrDtValoresJogador2.push(acwrDtMicrocicloJogador2);
    }
  
    return acwrDtValoresJogador2;
  };

  // Acumular valores de M% da carga externa DT para os gráficos
  const gerarValoresMdt = () => {
    const mDtValores = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número
  
    // Acessar os dados do M% para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const mDtMicrociclo = mDtData?.[i] || 0; // Pega o ACWR para cada microciclo
      mDtValores.push(mDtMicrociclo);
    }
  
    return mDtValores;
  };

  // Dados para a Carga Externa HS
  const labelsCargaExternaHS = [];
  const dadosCargaExternaHS = [];

  ordemDias.forEach((dia) => {
    if (cargaExternaHsData[dia]) {
      cargaExternaHsData[dia].forEach((treino) => {
        labelsCargaExternaHS.push(treino.data_treino);
        dadosCargaExternaHS.push(treino.distancia_hs || 0);
      });
    } else {
      labelsCargaExternaHS.push(dia);
      dadosCargaExternaHS.push(0); 
    }
  });

  const dataCargaExternaHS = {
    labels: labelsCargaExternaHS,
    datasets: [
      {
        label: "Carga Externa DT",
        data: dadosCargaExternaHS,
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        borderColor: "rgb(75, 192, 192)",
        borderWidth: 1,
      },
    ],
  };

  // Dados para a Carga Externa HS do Jogador 1
  const labelsCargaExternaHSJogador1 = [];
  const dadosCargaExternaHSJogador1 = [];

  ordemDias.forEach((dia) => {
    if (cargaExternaHsDataJogador1[dia]) {
      cargaExternaHsDataJogador1[dia].forEach((treino) => {
        labelsCargaExternaHSJogador1.push(treino.data_treino);
        dadosCargaExternaHSJogador1.push(treino.distancia_hs || 0);
      });
    } else {
      labelsCargaExternaHSJogador1.push(dia);
      dadosCargaExternaHSJogador1.push(0); 
    }
  });

  const dataCargaExternaHSJogador1 = {
    labels: labelsCargaExternaHSJogador1,
    datasets: [
      {
        label: "Carga Externa HS",
        data: dadosCargaExternaHSJogador1,
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        borderColor: "rgb(75, 192, 192)",
        borderWidth: 1,
      },
    ],
  };

  // Dados para a Carga Externa HS do Jogador 2
  const labelsCargaExternaHSJogador2 = [];
  const dadosCargaExternaHSJogador2 = [];

  ordemDias.forEach((dia) => {
    if (cargaExternaHsDataJogador2[dia]) {
      cargaExternaHsDataJogador2[dia].forEach((treino) => {
        labelsCargaExternaHSJogador2.push(treino.data_treino);
        dadosCargaExternaHSJogador2.push(treino.distancia_hs || 0);
      });
    } else {
      labelsCargaExternaHSJogador2.push(dia);
      dadosCargaExternaHSJogador2.push(0); 
    }
  });
  
  const dataCargaExternaHSJogador2 = {
    labels: labelsCargaExternaHSJogador2,
    datasets: [
      {
        label: "Carga Externa HS",
        data: dadosCargaExternaHSJogador2,
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        borderColor: "rgb(75, 192, 192)",
        borderWidth: 1,
      },
    ],
  };

  // Acumular valores de ACWR da carga externa HS para os gráficos
  const gerarValoresACWRhs = () => {
    const acwrHsValores = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número

  
    // Acessar os dados do ACWR para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const acwrHsMicrociclo = racioHsData?.[i] || 0; // Pega o ACWR para cada microciclo
      acwrHsValores.push(acwrHsMicrociclo);
    }
  
    return acwrHsValores;
  };

  // Acumular valores de ACWR da carga externa HS do jogador 1 para os gráficos
  const gerarValoresACWRhsJogador1 = () => {
    const acwrHsValoresJogador1 = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número

  
    // Acessar os dados do ACWR para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const acwrHsMicrocicloJogador1 = racioHsDataJogador1?.[i] || 0; // Pega o ACWR para cada microciclo
      acwrHsValoresJogador1.push(acwrHsMicrocicloJogador1);
    }
  
    return acwrHsValoresJogador1;
  };

  // Acumular valores de ACWR da carga externa HS do jogador 2 para os gráficos
  const gerarValoresACWRhsJogador2 = () => {
    const acwrHsValoresJogador2 = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número

  
    // Acessar os dados do ACWR para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const acwrHsMicrocicloJogador2 = racioHsDataJogador2?.[i] || 0; // Pega o ACWR para cada microciclo
      acwrHsValoresJogador2.push(acwrHsMicrocicloJogador2);
    }
  
    return acwrHsValoresJogador2;
  };

  // Acumular valores de M% da carga externa HS para os gráficos
  const gerarValoresMhs = () => {
    const mHsValores = [];
    const microcicloAtual = parseInt(microciclo); // Converter o microciclo atual para número
  
    // Acessar os dados do M% para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const mHsMicrociclo = mHsData?.[i] || 0; // Pega o ACWR para cada microciclo
      mHsValores.push(mHsMicrociclo);
    }
  
    return mHsValores;
  };

  // Acumular valores de monotonia para os gráficos
  const gerarValoresMonotonia = () => {
    const monotoniaValores = [];
    const microcicloAtual = parseInt(microciclo);
  
    // Acessar os dados da Monotonia para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const monotoniaMicrociclo = monotoniaData?.[i] || 0; // Pega a monotonia para cada microciclo
      monotoniaValores.push(monotoniaMicrociclo);
    }
  
    return monotoniaValores;
  };

  // Acumular valores de strain para os gráficos
  const gerarValoresStrain = () => {
    const strainValores = [];
    const microcicloAtual = parseInt(microciclo);
  
    // Acessar os dados de Strain para o microciclo selecionado e os anteriores
    for (let i = 1; i <= microcicloAtual; i++) {
      const strainMicrociclo = strainData?.[i] || 0; // Pega a monotonia para cada microciclo
      strainValores.push(strainMicrociclo);
    }
  
    return strainValores;
  };

  // Criar lista do Tipo de Análise
  const tipo_analise = ["Individual", "Comparativa"]

  // Criar gráfico para o Z-score
  const zScoreData = {
    labels: ["Z-Score"],
    datasets: [
      {
        label: "Z-Score ACWR PSE",
        data: [zScorePSE?.z_score || 0],
        backgroundColor: "rgba(255, 99, 132, 0.6)",
        borderColor: "rgba(243, 166, 183, 0.6)",
        borderWidth: 1,
      },
      {
        label: "Z-Score ACWR DT",
        data: [zScoreDT?.z_score || 0],
        backgroundColor: "rgba(54, 162, 235, 0.6)",
        borderColor: "rgba(130, 193, 235, 0.6)",
        borderWidth: 1,
      },
      {
        label: "Z-Score Wellness",
        data: [zScoreWellness?.z_score || 0],
        backgroundColor: "rgba(255, 206, 86, 0.6)",
        borderColor: "rgba(246, 220, 156, 0.6)",
        borderWidth: 1,
      },
      {
        label: "Z-Score Monotonia",
        data: [zScoreMonotonia?.z_score || 0],
        backgroundColor: "rgba(75, 192, 192, 0.6)",
        borderColor: "rgba(130, 191, 191, 0.6)",
        borderWidth: 1,
      },
      {
        label: "Z-Score Strain",
        data: [zScoreStrain?.z_score || 0],
        backgroundColor: "rgba(153, 102, 255, 0.6)",
        borderColor: "rgba(182, 156, 234, 0.6)",
        borderWidth: 1,
      },
    ],  
  };

  // Acumular valores de CMJ para os gráficos
  const [cmjValores, setCMJValores] = useState([]);

  useEffect(() => {
    const fetchCMJValores = async () => {
      const valores = [];
      for (let i = 1; i <= microciclo; i++) {

        try {
          const response = await fetch(`http://127.0.0.1:5000/api/cmj/${jogador}/${i}`);
          const data = await response.json();
          valores.push(data.CMJ || 0);
        } catch (error) {
          console.error(`Erro ao buscar CMJ para microciclo ${i}:`, error);
          valores.push(0); // Caso haja erro, adiciona 0 como fallback
        }
      }
      setCMJValores(valores);
    };

    if (jogador && microciclo) {
      fetchCMJValores();
    }
  }, [jogador, microciclo]); // Atualiza quando o jogador ou microciclo mudar

  // Acumular valores de SJ para os gráficos
  const [sjValores, setSJValores] = useState([]);

  useEffect(() => {
    const fetchSJValores = async () => {
      const valores = [];
      for (let i = 1; i <= microciclo; i++) {

        try {
          const response = await fetch(`http://127.0.0.1:5000/api/sj/${jogador}/${i}`);
          const data = await response.json();
          valores.push(data.SJ || 0);
        } catch (error) {
          console.error(`Erro ao buscar CMJ para microciclo ${i}:`, error);
          valores.push(0); // Caso haja erro, adiciona 0 como fallback
        }
      }
      setSJValores(valores);
    };

    if (jogador && microciclo) {
      fetchSJValores();
    }
  }, [jogador, microciclo]); // Atualiza quando o jogador ou microciclo mudar

  // Acumular valores de CMJ para os gráficos do jogador 1
  const [cmjValoresJogador1, setCMJValoresJogador1] = useState([]);

  useEffect(() => {
    const fetchCMJValoresJogador1 = async () => {
      const valores = [];
      for (let i = 1; i <= microciclo; i++) {

        try {
          const response = await fetch(`http://127.0.0.1:5000/api/cmj/${jogador1}/${i}`);
          const data = await response.json();
          valores.push(data.CMJ || 0);
        } catch (error) {
          console.error(`Erro ao buscar CMJ para microciclo ${i}:`, error);
          valores.push(0); // Caso haja erro, adiciona 0 como fallback
        }
      }
      setCMJValoresJogador1(valores);
    };

    if (jogador1 && microciclo) {
      fetchCMJValoresJogador1();
    }
  }, [jogador1, microciclo]); // Atualiza quando o jogador ou microciclo mudar

  // Acumular valores de SJ para os gráficos do Jogador 1
  const [sjValoresJogador1, setSJValoresJogador1] = useState([]);

  useEffect(() => {
    const fetchSJValoresJogador1 = async () => {
      const valores = [];
      for (let i = 1; i <= microciclo; i++) {

        try {
          const response = await fetch(`http://127.0.0.1:5000/api/sj/${jogador1}/${i}`);
          const data = await response.json();
          valores.push(data.SJ || 0);
        } catch (error) {
          console.error(`Erro ao buscar CMJ para microciclo ${i}:`, error);
          valores.push(0); // Caso haja erro, adiciona 0 como fallback
        }
      }
      setSJValoresJogador1(valores);
    };

    if (jogador1 && microciclo) {
      fetchSJValoresJogador1();
    }
  }, [jogador1, microciclo]); // Atualiza quando o jogador ou microciclo mudar

  // Acumular valores de CMJ para os gráficos do jogador 2
  const [cmjValoresJogador2, setCMJValoresJogador2] = useState([]);

  useEffect(() => {
    const fetchCMJValoresJogador2 = async () => {
      const valores = [];
      for (let i = 1; i <= microciclo; i++) {

        try {
          const response = await fetch(`http://127.0.0.1:5000/api/cmj/${jogador2}/${i}`);
          const data = await response.json();
          valores.push(data.CMJ || 0);
        } catch (error) {
          console.error(`Erro ao buscar CMJ para ${i}:`, error);
          valores.push(0); // Caso haja erro, adiciona 0 como fallback
        }
      }
      setCMJValoresJogador2(valores);
    };

    if (jogador2 && microciclo) {
      fetchCMJValoresJogador2();
    }
  }, [jogador2, microciclo]); // Atualiza quando o jogador ou microciclo mudar

  // Acumular valores de SJ para os gráficos do Jogador 2
  const [sjValoresJogador2, setSJValoresJogador2] = useState([]);

  useEffect(() => {
    const fetchSJValoresJogador2 = async () => {
      const valores = [];
      for (let i = 1; i <= microciclo; i++) {

        try {
          const response = await fetch(`http://127.0.0.1:5000/api/sj/${jogador2}/${i}`);
          const data = await response.json();
          valores.push(data.SJ || 0);
        } catch (error) {
          console.error(`Erro ao buscar CMJ para microciclo ${i}:`, error);
          valores.push(0); // Caso haja erro, adiciona 0 como fallback
        }
      }
      setSJValoresJogador2(valores);
    };

    if (jogador2 && microciclo) {
      fetchSJValoresJogador2();
    }
  }, [jogador2, microciclo]); // Atualiza quando o jogador ou microciclo mudar

  
  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Instrumento de Monitorização</h1>

      {/* Tipo de Análise*/}
      <label style={{ fontSize: "18px", marginRight: "10px" }}>
        Tipo de Análise:
      </label>
      <select
        value={tipoAnalise}
        onChange={(e) => setTipoAnalise(e.target.value)}
        style={{ padding: "8px", fontSize: "16px", marginBottom: "30px"}}
      >
        <option value="">Selecione o tipo de análise</option>
        {tipo_analise.map((nome, index) => (
          <option key={index} value={nome}>
            {nome}
          </option>
        ))}
      </select>

      {tipoAnalise === "Individual" && (
        <div>
          {/* Seleção do jogador */}
          <label style={{ fontSize: "18px", marginRight: "10px" }}>
            Jogador:
          </label>
          <select
            value={jogador}
            onChange={(e) => setJogador(e.target.value)}
            style={{ padding: "8px", fontSize: "16px"}}
          >
            <option value="">Selecione um jogador</option>
            {jogadores.map((nome, index) => (
              <option key={index} value={nome}>
                {nome}
              </option>
            ))}
          </select>

          {/* Seleção do microciclo */}
          <label style={{ fontSize: "18px", marginLeft: "20px", marginRight:"10px" }}>
            Microciclo:
          </label>
          <select
            value={microciclo}
            onChange={(e) => setMicrociclo(e.target.value)}
            style={{ padding: "8px", fontSize: "16px" }}
          >
            {microciclos.map((mc) => (
              <option key={mc} value={mc}>
                Microciclo {mc}
              </option>
            ))}
          </select>

          {/* Seleção da Variável */}
          <label style={{ fontSize: "18px", marginLeft: "20px", marginRight: "10px" }}>Variável:</label>
          <select value={variavel} onChange={(e) => setVariavel(e.target.value)} style={{ padding: "8px", fontSize: "16px" }}>
            <option value="Wellness">Wellness</option>
            <option value="PSE">PSE</option>
            <option value="Carga de Treino">Carga de Treino</option>
            <option value="Monotonia & Strain">Monotonia & Strain</option>
            <option value="Z-score">Z-score</option>
            <option value="CMJ & SJ">CMJ & SJ</option>
          </select>       


          {/* Exibir a análise Wellness */}
          {jogador && variavel === "Wellness" && (
            <div style={{ marginTop: "20px" }}>
              <h2>Wellness </h2>
              <h3>Estado de prontidão da atleta {jogador} {obterIntervaloDatas()}</h3>
              
              {wellness ? (
                <div>
                <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '20px' }}>
                  {ordemDias.map((dia, index) => (
                    <div key={index} style={{ textAlign: "left", margin: '0 10px' }}>
                      <h4 style={{ textDecoration: "underline", fontSize: "20px", fontWeight: "bold" }}>{dia}</h4>
                      {["sono", "fadiga", "dor_muscular", "stress"].map((variavel) => (
                        <p key={variavel} style={verificarAlertaWellness(wellness[dia]?.[variavel] || 0)}>
                          <strong>{variavel.charAt(0).toUpperCase() + variavel.slice(1).replace("_", " ")}:</strong> {wellness[dia]?.[variavel] || 0} {(wellness[dia]?.[variavel] || 0) >= 6 ? "⚠️" : ""}
                        </p>
                      ))}
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: "20px", color: "orange", fontWeight: "bold" }}>
                  {ordemDias.some(dia => ["sono", "fadiga", "dor_muscular", "stress"].some(variavel => (wellness[dia]?.[variavel] || 0) >= 6)) && <p>⚠️ Atenção: Há valores elevados em algumas variáveis!</p>}
                </div>

                  {/* Contêiner para os gráficos lado a lado */}
                  <div style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "20px" }}>

                    {/* Gráfico de Bem-Estar */}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar data={dataWellness} options={{ ...tamanho, plugins: { title: { display: true, text: "Valores das Variáveis por Dia da Semana" } } }} /> 
                    </div>

                    {/* Gráfico das Médias */}
                    <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "40px" }}>
                      <Bar data={dataMedias} options={{ ...tamanho, plugins: { title: { display: true, text: "Média do Valor das Variáveis por Semana" } } }} />
                    </div>
                  </div>
                </div>
              ) : (
                <p>A carregar os dados do Wellness...</p>
              )}
            </div>
          )}

          {/* Exibir a análise PSE*/}
          {jogador && variavel === "PSE" && (
            <div style={{ marginTop: "20px" }}>
              <h2>Perceção Subjetiva de Esforço</h2>
              <h3>Perceção da atleta {jogador} {obterIntervaloDatasPse()}</h3>

              {pseData && Object.keys(pseData).length > 0 ? (
                <div>
                  {/* Lista de treinos */}
                  <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '20px' }}>
                    {ordemDias.map((dia, index) => (
                      <div key={index} style={{ textAlign: "left", margin: '0 10px' }}>
                        <h4 style={{ textDecoration: "underline", fontSize: "20px", fontWeight: "bold" }}>
                          {dia} 
                        </h4>

                        {pseData[dia] ? (
                          pseData[dia].map((treino, idx) => (
                            <div key={idx} style={{ textAlign: "left" }}>
                              <p><strong>Data:</strong> {formatarDataPse(treino.data_treino)}</p>
                              <p style={verificarAlertaPSE(parseFloat(treino.pse) || 0)}>
                                <strong>PSE:</strong> {treino.pse} {parseFloat(treino.pse) >= 9 ? "⚠️" : ""}
                              </p>
                            </div>
                          ))
                        ) : (
                          <p>Sem treino/jogo</p>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Alertas de valores altos */}
                  <div style={{ marginTop: "20px", color: "orange", fontWeight: "bold", textAlign: "center" }}>
                    {Object.values(pseData).some(dia => dia.some(treino => parseFloat(treino.pse) >= 9)) && (
                      <p>⚠️ Atenção: Há valores elevados na PSE!</p>
                    )}
                  </div>

                  {/* Contêiner para o gráfico PSE */}
                  <div style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "20px" }}>
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar data={dataPSE} options={{ ...tamanho, plugins: { title: { display: true, text: "PSE por Treino" } } }} />
                    </div>
                  </div>
                </div>
              ) : (
                <p>A carregar os dados da PSE...</p>     
              )}
            </div>
          )}

          {/* Exibir a análise Carga de Treino*/}
          {jogador && variavel === "Carga de Treino" && (
            <div style={{ marginTop: "20px" }}>
              <h2>Carga de Treino</h2>

              {/* Exibir a análise Carga Interna*/}
              <h3>Carga Interna da atleta {jogador} {obterIntervaloDatasPse()}</h3>

              {cargaInternaData && Object.keys(cargaInternaData).length > 0 ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '20px' }}>
                    {ordemDias.map((dia, index) => (
                      <div key={index} style={{ textAlign: "left", margin: '0 10px' }}>
                        <h4 style={{ textDecoration: "underline", fontSize: "20px", fontWeight: "bold" }}>{dia}</h4>

                        {cargaInternaData[dia] ? (
                          cargaInternaData[dia].map((treino, idx) => (
                            <div key={idx} style={{textAlign: "left"}}>
                              <p>
                                <strong>Data:</strong> {formatarDataPse(treino.data_treino)}
                              </p>
                              <p>
                                <strong>Duração (min):</strong> {treino.duracao_treino}
                              </p>
                              <p>
                                <strong>Carga da Sessão:</strong> {treino.carga_interna}
                              </p>
                            </div>
                          ))
                        ) : (
                          <p>Sem treino/jogo</p>
                        )}             
                      </div>
                    ))}
                  </div>

                  {/* Exibir o ACWR (AWCR) uma única vez, antes dos gráficos */}
                  <div style={{ textAlign: "center", marginBottom: "20px" }}>
                    <h3 style={{color:"green"}}>ACWR PSE: {racioData?.[parseInt(microciclo)] || 0}</h3> {/* Ajustado para acessar pelo número do microciclo */}
                  </div>

                  {/* Contêiner para os gráficos lado a lado */}
                  <div style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "20px" }}>
              
                    {/* Contêiner para o gráfico Carga Interna */}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar data={dataCargaInterna} options={{ ...tamanho, plugins: { title: { display: true, text: "Carga Interna Diária" } } }} />
                    </div>
                
                    {/* Gráfico acumulado de ACWR */}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar 
                        data={{
                          labels: Array.from({ length:microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                          datasets: [
                            {
                              label: "ACWR",
                              data: gerarValoresACWR(),
                              backgroundColor: "rgba(105, 235, 54, 0.5)",
                              borderColor: "rgb(114, 235, 54)",
                              borderWidth: 1
                            }
                          ]
                        }}
                        options={{
                          ...tamanho,
                          plugins: { title: { display: true, text: "ACWR da Carga Interna por Microciclo" } }
                        }}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <p>A carregar os dados da Carga Interna...</p>
              )}

              {/* Exibir a análise Carga Externa DT*/}
              <h3 style={{ marginTop: "80px" }}>Carga Externa da atleta {jogador} para a Distância Total {obterIntervaloDatasPse()} </h3>

              {cargaExternaDtData && Object.keys(cargaExternaDtData).length > 0 ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '20px' }}>
                    {ordemDias.map((dia, index) => (
                      <div key={index} style={{ textAlign: "left", margin: '0 10px' }}>
                        <h4 style={{ textDecoration: "underline", fontSize: "20px", fontWeight: "bold" }}>{dia}</h4>

                        {cargaExternaDtData[dia] ? (
                          cargaExternaDtData[dia].map((treino, idx) => (
                            <div key={idx} style={{textAlign:"left"}}>
                              <p>
                              <strong>Data:</strong> {formatarDataPse(treino.data_treino)}
                              </p> 
                              <p>
                              <strong>Distância Total:</strong> {treino.distancia_total}
                              </p> 
                            </div>
                          ))
                        ) : (
                          <p> Sem treino/jogo </p>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Exibir o ACWR (AWCR) uma única vez, antes dos gráficos */}
                  <div style={{ textAlign: "center", marginBottom: "20px" }}>
                    <h3 style={{color:"green"}}>ACWR DT: {racioDtData[microciclo] || 0}</h3> {/* Este é o valor do ACWR, exibido apenas uma vez */}
                    <h3 style={{color:"orange"}}>M% DT: {mDtData[microciclo] || 0}</h3> {/* Este é o valor do M%, exibido apenas uma vez */}
                  </div>

                  {/* Contêiner para os gráficos lado a lado */}
                  <div style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "20px" }}>
              
                    {/* Contêiner para o gráfico Carga Externa DT */}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar data={dataCargaExternaDT} options={{ ...tamanho, plugins: { title: { display: true, text: "Carga Externa Diária com a Distância Total Percorrida" } } }} />
                    </div>
                
                    {/* Gráfico acumulado de ACWR */}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar 
                        data={{
                          labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                          datasets: [
                            {
                              label: "ACWR DT",
                              data: gerarValoresACWRdt(),
                              backgroundColor: "rgba(105, 235, 54, 0.5)",
                              borderColor: "rgb(114, 235, 54)",
                              borderWidth: 1
                            }
                          ]
                        }}
                        options={{
                          ...tamanho,
                          plugins: { title: { display: true, text: "ACWR da Distância Total Percorrida por Microciclo" } }
                        }}
                      />
                    </div>

                    {/* Gráfico do M%*/}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar 
                        data={{
                          labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                          datasets: [
                            {
                              label: "M% DT",
                              data: gerarValoresMdt(),
                              backgroundColor: "rgba(241, 177, 16, 0.68)",
                              borderColor: "rgb(255, 206, 86)",
                              borderWidth: 1
                            }
                          ]
                        }}
                        options={{
                          ...tamanho,
                          plugins: { title: { display: true, text: "M% da Distância Total Percorrida por Microciclo" } }
                        }}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <p>A carregar os dados da Carga Externa DT...</p>
              )}

              {/* Exibir a análise Carga Externa HS*/}
              <h3 style={{ marginTop: "80px" }}>Carga Externa da atleta {jogador} para a Distância em Alta Velocidade {obterIntervaloDatasPse()}</h3>

              {cargaExternaHsData && Object.keys(cargaExternaHsData).length > 0 ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-around', marginBottom: '20px' }}>
                    {ordemDias.map((dia, index) => (
                      <div key={index} style={{ textAlign: "left", margin: '0 10px' }}>
                        <h4 style={{ textDecoration: "underline", fontSize: "20px", fontWeight: "bold" }}>{dia}</h4>

                        {cargaExternaHsData[dia] ? (
                          cargaExternaHsData[dia].map((treino, idx) => (
                            <div key={idx} style={{textAlign:"left"}}>
                              <p>
                              <strong>Data:</strong> {formatarDataPse(treino.data_treino)}
                              </p> 
                              <p>
                              <strong>Distância em Alta Velocidade:</strong> {treino.distancia_hs}
                              </p> 
                            </div>
                          ))
                        ) : (
                          <p> Sem treino/jogo </p>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Exibir o ACWR (AWCR) uma única vez, antes dos gráficos */}
                  <div style={{ textAlign: "center", marginBottom: "20px" }}>
                    <h3 style={{color:"green"}}>ACWR HS: {racioHsData[microciclo] || 0}</h3> {/* Este é o valor do ACWR, exibido apenas uma vez */}
                    <h3 style={{color:"orange"}}>M% HS: {mHsData[microciclo] || 0}</h3> {/* Este é o valor do M%, exibido apenas uma vez */}
                  </div>

                  {/* Contêiner para os gráficos lado a lado */}
                  <div style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "20px" }}>
              
                    {/* Contêiner para o gráfico Carga Externa HS */}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar data={dataCargaExternaHS} options={{ ...tamanho, plugins: { title: { display: true, text: "Carga Externa Diária com a Distância Percorrida em Alta Velocidade" } } }} />
                    </div>
                
                    {/* Gráfico acumulado de ACWR */}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar 
                        data={{
                          labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                          datasets: [
                            {
                              label: "ACWR HS",
                              data: gerarValoresACWRhs(),
                              backgroundColor: "rgba(105, 235, 54, 0.5)",
                              borderColor: "rgb(114, 235, 54)",
                              borderWidth: 1
                            }
                          ]
                        }}
                        options={{
                          ...tamanho,
                          plugins: { title: { display: true, text: "ACWR da Distância Percorrida em Alta Velocidade por Microciclo" } }
                        }}
                      />
                    </div>

                    {/* Gráfico do M%*/}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar 
                        data={{
                          labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                          datasets: [
                            {
                              label: "M% HS",
                              data: gerarValoresMhs(),
                              backgroundColor: "rgba(241, 177, 16, 0.68)",
                              borderColor: "rgb(255, 206, 86)",
                              borderWidth: 1
                            }
                          ]
                        }}
                        options={{
                          ...tamanho,
                          plugins: { title: { display: true, text: "M% HS por Microciclo" } }
                        }}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <p>A carregar os dados da Carga Externa HS...</p>
              )}
            </div>
          )}

          {/* Exibir a análise Monotonia & Strain*/}
          {jogador && variavel === "Monotonia & Strain" && (
            <div style={{ marginTop: "20px" }}>
              <h2>Monotonia & Strain</h2>
              <h3>Monotonia e Strain da atleta {jogador} no Microciclo {microciclo}</h3>
              {monotoniaData ? (
                <div>
                  <div style={{ textAlign: "center", marginBottom: "20px" }}>
                    <h3 style={{color:"green"}}>Monotonia: {monotoniaData?.[parseInt(microciclo)] || 0}</h3> 
                    <h3 style={{color:"orange"}}>Strain: {strainData ? strainData?.[parseInt(microciclo)]|| 0 : 0}</h3> 
                  </div>

                  {/* Contêiner para os gráficos lado a lado */}
                  <div style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "20px" }}>

                    {/* Gráfico acumulado de Monotonia */}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar 
                        data={{
                          labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                          datasets: [
                            {
                              label: "Monotonia por Microciclo",
                              data: gerarValoresMonotonia(),
                              backgroundColor: "rgba(105, 235, 54, 0.5)",
                              borderColor: "rgb(114, 235, 54)",
                              borderWidth: 1
                            }
                          ]
                        }}
                        options={{
                          ...tamanho,
                          plugins: { title: { display: true, text: "Monotonia por Microciclo" } }
                        }}
                      />
                    </div>

                    {/* Gráfico do Strain*/}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar 
                        data={{
                          labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                          datasets: [
                            {
                              label: "Strain por Microciclo",
                              data: gerarValoresStrain(),
                              backgroundColor: "rgba(241, 177, 16, 0.68)",
                              borderColor: "rgb(255, 206, 86)",
                              borderWidth: 1
                            }
                          ]
                        }}
                        options={{
                          ...tamanho,
                          plugins: { title: { display: true, text: "Strain por Microciclo" } }
                        }}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <p>A carregar os dados de Monotonia & Strain...</p>
              )}
            </div>
          )}

          {/* Exibir a análise Z-score*/}
          {jogador && variavel === "Z-score" && (
            <div style={{ marginTop: "20px" }}>
              <h2>Z-score</h2>
              <h3>Z-score das diferentes variáveis da atleta {jogador}</h3>
              {/* Contêiner para os gráficos lado a lado */}
              <div style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "30px" }}>
                <div style={{ marginTop: "50px", marginLeft: "150px" }}>
                  {zScorePSE ? (
                    <div>
                      <div style={{ textAlign: "center", marginBottom: "20px" }}>
                        <p> <strong>Z-score ACWR PSE:</strong> {zScorePSE.z_score || 0}</p>                     
                      </div>
                    </div>
                  ) : (
                    <p>A carregar os dados de Z-score ACWR PSE...</p>
                  )}

                  {zScoreDT ? (
                    <div>
                      <div style={{ textAlign: "center", marginBottom: "20px" }}>
                        <p> <strong>Z-score ACWR DT:</strong> {zScoreDT.z_score || 0}</p>                     
                      </div>
                    </div>
                  ) : (
                    <p>A carregar os dados de Z-score ACWR DT...</p>
                  )}

                  {zScoreWellness ? (
                    <div>
                      <div style={{ textAlign: "center", marginBottom: "20px" }}>
                        <p> <strong>Z-score Wellness:</strong> {zScoreWellness.z_score || 0}</p>                     
                      </div>
                    </div>
                  ) : (
                    <p>A carregar os dados de Z-score Wellness...</p>
                  )}

                  {zScoreMonotonia ? (
                    <div>
                      <div style={{ textAlign: "center", marginBottom: "20px" }}>
                        <p> <strong>Z-score Monotonia:</strong> {zScoreMonotonia.z_score || 0}</p>                     
                      </div>
                    </div>
                  ) : (
                    <p>A carregar os dados de Z-score Monotonia...</p>
                  )}

                  {zScoreStrain ? (
                    <div>
                      <div style={{ textAlign: "center", marginBottom: "20px" }}>
                        <p> <strong>Z-score Strain:</strong> {zScoreStrain.z_score || 0}</p>                     
                      </div>
                    </div>
                  ) : (
                    <p>A carregar os dados de Z-score Strain...</p>
                  )}
                </div>
                <div style={{ width: "500px", height: "300px", marginLeft: "50px" }}>
                    <Bar data={zScoreData} options={{ ...tamanho, plugins: { title: { display: true, text: "Valores do Z-score para cada Variável por Semana" } } }}  />
                </div>
              </div>
            </div>
          )}

          {/* Exibir a análise CMJ & SJ*/}
          {jogador && variavel === "CMJ & SJ" && (
            <div style={{ marginTop: "20px" }}>
              <h2>CMJ & SJ</h2>

              {/* Exibir a análise Carga Interna*/}
              <h3>CMJ & SJ da atleta {jogador}</h3>

              {cmjData && sjData ? (
                <div>
                  <div style={{ textAlign: "center", marginBottom: "20px" }}>
                    <h3 style={{color:"green"}}>CMJ: {cmjData.CMJ || 0}</h3> 
                    <h3 style={{color:"orange"}}>SJ: {sjData.SJ || 0}</h3> 
                  </div>
                
                  {/* Contêiner para os gráficos lado a lado */}
                  <div style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "20px" }}>

                    {/* Gráfico acumulado de CMJ */}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar 
                        data={{
                          labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                          datasets: [
                            {
                              label: "CMJ por Microciclo",
                              data: cmjValores,
                              backgroundColor: "rgba(105, 235, 54, 0.5)",
                              borderColor: "rgb(114, 235, 54)",
                              borderWidth: 1
                            }
                          ]
                        }}
                        options={{
                          ...tamanho,
                          plugins: { title: { display: true, text: "CMJ por Microciclo" } }
                        }}
                      />
                    </div>

                    {/* Gráfico do SJ*/}
                    <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                      <Bar 
                        data={{
                          labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                          datasets: [
                            {
                              label: "SJ por Microciclo",
                              data: sjValores,
                              backgroundColor: "rgba(241, 177, 16, 0.68)",
                              borderColor: "rgb(255, 206, 86)",
                              borderWidth: 1
                            }
                          ]
                        }}
                        options={{
                          ...tamanho,
                          plugins: { title: { display: true, text: "SJ por Microciclo" } }
                        }}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <p>A carregar os dados de CMJ e SJ...</p>
              )}
            </div>          
          )}
        </div>
      )}

      {tipoAnalise === "Comparativa" && (
        <div>
          <div style={{ textAlign: "center"}}>

            {/* Seleção do microciclo */}
            <label style={{ fontSize: "18px", marginLeft: "20px", marginRight:"10px" }}>
              Microciclo:
            </label>
            <select
              value={microciclo}
              onChange={(e) => setMicrociclo(e.target.value)}
              style={{ padding: "8px", fontSize: "16px" }}
            >
              {microciclos.map((mc) => (
                <option key={mc} value={mc}>
                  Microciclo {mc}
                </option>
              ))}
            </select>

            {/* Seleção da Variável */}
            <label style={{ fontSize: "18px", marginLeft: "20px", marginRight: "10px" }}>Variável:</label>
            <select value={variavel} onChange={(e) => setVariavel(e.target.value)} style={{ padding: "8px", fontSize: "16px" }}>
              <option value="Wellness">Wellness</option>
              <option value="PSE">PSE</option>
              <option value="Carga de Treino">Carga de Treino</option>
              <option value="CMJ & SJ">CMJ & SJ</option>          
            </select> 
          </div>

          {variavel === "Wellness" && (
            <div style={{ marginTop: "30px" }}>
              <h2>Wellness </h2>

              {/* Contêiner para os dados lado a lado */}
              <div style={{ display: "flex", justifyContent: "center", gap: "100px", marginTop: "20px" }}>
                <div>
                  {/* Seleção do jogador 1 */}
                  <label style={{ fontSize: "18px", marginRight: "10px" }}>
                    Jogador 1:
                  </label>
                  <select
                    value={jogador1}
                    onChange={(e) => setJogador1(e.target.value)}
                    style={{ padding: "8px", fontSize: "16px"}}
                  >
                    <option value="">Selecione um jogador</option>
                    {jogadores.map((nome, index) => (
                      <option key={index} value={nome}>
                        {nome}
                      </option>
                    ))}
                  </select>

                  {/* Exibir a análise Wellness para o jogador 1 */}
                  {jogador1 && (
                    <div style={{ marginTop: "20px" }}>
                      <h3>Estado de prontidão da atleta {jogador1} {obterIntervaloDatas()}</h3>

                      {wellnessJogador1 ? (
                        <div> 
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "40px" }}>
                            <Bar data={dataMediasJogador1} options={{ ...tamanho, plugins: { title: { display: true, text: "Média do Valor das Variáveis por Semana" } } }} />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados do Wellness para o jogador 1...</p>
                      )}
                    </div>
                  )}
                </div>

                <div>
                  {/* Seleção do jogador 2 */}
                  <label style={{ fontSize: "18px", marginLeft: "20px", marginRight: "10px"}}>
                    Jogador 2:
                  </label>
                  <select
                    value={jogador2}
                    onChange={(e) => setJogador2(e.target.value)}
                    style={{ padding: "8px", fontSize: "16px"}}
                  >
                    <option value="">Selecione um jogador</option>
                    {jogadores.map((nome, index) => (
                      <option key={index} value={nome}>
                        {nome}
                      </option>
                    ))}
                  </select>

                  {/* Exibir a análise Wellness para o jogador 2 */}
                  {jogador2 && (
                    <div style={{ marginTop: "20px" }}>
                      <h3>Estado de prontidão da atleta {jogador2} {obterIntervaloDatas()}</h3>

                      {wellnessJogador2 ? (
                        <div>
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "40px" }}>
                            <Bar data={dataMediasJogador2} options={{ ...tamanho, plugins: { title: { display: true, text: "Média do Valor das Variáveis por Semana" } } }} />
                          </div>
                        </div>                  
                      ) : (
                        <p>A carregar os dados do Wellness para o jogador 2...</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>   
          )}    

          {variavel === "PSE" && (
            <div style={{ marginTop: "30px" }}>
              <h2>Perceção Subjetiva de Esforço </h2>

              {/* Contêiner para os dados lado a lado */}
              <div style={{ display: "flex", justifyContent: "center", gap: "100px", marginTop: "20px" }}>
                <div>
                  {/* Seleção do jogador 1 */}
                  <label style={{ fontSize: "18px", marginRight: "10px" }}>
                    Jogador 1:
                  </label>
                  <select
                    value={jogador1}
                    onChange={(e) => setJogador1(e.target.value)}
                    style={{ padding: "8px", fontSize: "16px"}}
                  >
                    <option value="">Selecione um jogador</option>
                    {jogadores.map((nome, index) => (
                      <option key={index} value={nome}>
                        {nome}
                      </option>
                    ))}
                  </select>

                  {/* Exibir a análise PSE para o jogador 1 */}
                  {jogador1 && (
                    <div style={{ marginTop: "20px" }}>
                      <h3>Perceção da atleta {jogador1}</h3>

                      {pseDataJogador1 ? (
                        <div> 
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "40px" }}>
                            <Bar data={dataPSEJogador1} options={{ ...tamanho, plugins: { title: { display: true, text: "PSE por Treino" } } }} />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados da PSE para o jogador 1...</p>
                      )}
                    </div>
                  )}
                </div>

                <div>
                  {/* Seleção do jogador 2 */}
                  <label style={{ fontSize: "18px", marginLeft: "20px", marginRight: "10px"}}>
                    Jogador 2:
                  </label>
                  <select
                    value={jogador2}
                    onChange={(e) => setJogador2(e.target.value)}
                    style={{ padding: "8px", fontSize: "16px"}}
                  >
                    <option value="">Selecione um jogador</option>
                    {jogadores.map((nome, index) => (
                      <option key={index} value={nome}>
                        {nome}
                      </option>
                    ))}
                  </select>

                  {/* Exibir a análise PSE para o jogador 2 */}
                  {jogador2 && (
                    <div style={{ marginTop: "20px" }}>
                      <h3>Perceção da atleta {jogador2}</h3>

                      {pseDataJogador2 ? (
                        <div>
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "40px" }}>
                            <Bar data={dataPSEJogador2} options={{ ...tamanho, plugins: { title: { display: true, text: "PSE por Treino" } } }} />
                          </div>
                        </div>                  
                      ) : (
                        <p>A carregar os dados da PSE para o jogador 2...</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>   
          )}  

          {variavel === "Carga de Treino" && (
            <div style={{ marginTop: "30px" }}>
              <h2>Carga de Treino </h2>

              {/* Contêiner para os dados lado a lado */}
              <div style={{ display: "flex", justifyContent: "center", gap: "100px", marginTop: "20px" }}>
                <div>
                  {/* Seleção do jogador 1 */}
                  <label style={{ fontSize: "18px", marginRight: "10px" }}>
                    Jogador 1:
                  </label>
                  <select
                    value={jogador1}
                    onChange={(e) => setJogador1(e.target.value)}
                    style={{ padding: "8px", fontSize: "16px"}}
                  >
                    <option value="">Selecione um jogador</option>
                    {jogadores.map((nome, index) => (
                      <option key={index} value={nome}>
                        {nome}
                      </option>
                    ))}
                  </select>

                  {/* Exibir a análise Carga de Treino para o jogador 1 */}
                  {jogador1 && (
                    <div style={{ marginTop: "20px" }}>
                      <h3 style={{ marginTop: "40px" }}>Carga Interna da atleta {jogador1}</h3>

                      {cargaInternaDataJogador1 ? (
                        <div> 
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "20px" }}>
                            <Bar data={dataCargaInternaJogador1} options={{ ...tamanho, plugins: { title: { display: true, text: "Carga Interna Diária" } } }} />
                          </div>                        

                          {/* Gráfico acumulado de ACWR */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop:"40px" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "ACWR",
                                    data: gerarValoresACWRJogador1(),
                                    backgroundColor: "rgba(105, 235, 54, 0.5)",
                                    borderColor: "rgb(114, 235, 54)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "ACWR da Carga Interna por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados da Carga Interna para o jogador 1...</p>
                      )}

                      <h3 style={{ marginTop: "50px" }}>Carga Externa DT da atleta {jogador1}</h3>
                      {cargaExternaDtDataJogador1 ? (
                        <div> 
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "20px" }}>
                            <Bar data={dataCargaExternaDTJogador1} options={{ ...tamanho, plugins: { title: { display: true, text: "Carga Externa Diária com a Distância Total Percorrida" } } }} />
                          </div>

                          {/* Gráfico acumulado de ACWR */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop:"40px" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "ACWR DT",
                                    data: gerarValoresACWRdtJogador1(),
                                    backgroundColor: "rgba(105, 235, 54, 0.5)",
                                    borderColor: "rgb(114, 235, 54)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "ACWR da Distância Total Percorrida por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados da Carga Externa DT para o jogador 1...</p>
                      )}

                      <h3 style={{ marginTop: "50px" }}>Carga Externa HS da atleta {jogador1}</h3>
                      {cargaExternaHsDataJogador1 ? (
                        <div> 
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "20px" }}>
                            <Bar data={dataCargaExternaHSJogador1} options={{ ...tamanho, plugins: { title: { display: true, text: "Carga Externa Diária com a Distância Percorrida em Alta Velocidade" } } }} />
                          </div>

                          {/* Gráfico acumulado de ACWR */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop:"40px" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "ACWR HS",
                                    data: gerarValoresACWRhsJogador1(),
                                    backgroundColor: "rgba(105, 235, 54, 0.5)",
                                    borderColor: "rgb(114, 235, 54)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "ACWR da Distância Percorrida em Alta Velocidade por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados da Carga Externa HS para o jogador 1...</p>
                      )}
                    </div>
                  )}
                </div>

                <div>
                  {/* Seleção do jogador 2 */}
                  <label style={{ fontSize: "18px", marginLeft: "20px", marginRight: "10px"}}>
                    Jogador 2:
                  </label>
                  <select
                    value={jogador2}
                    onChange={(e) => setJogador2(e.target.value)}
                    style={{ padding: "8px", fontSize: "16px"}}
                  >
                    <option value="">Selecione um jogador</option>
                    {jogadores.map((nome, index) => (
                      <option key={index} value={nome}>
                        {nome}
                      </option>
                    ))}
                  </select>

                  {/* Exibir a análise Carga de Treino para o jogador 2 */}
                  {jogador2 && (
                    <div style={{ marginTop: "20px" }}>
                      <h3 style={{ marginTop: "40px" }}>Carga Interna da atleta {jogador2}</h3>

                      {cargaInternaDataJogador2 ? (
                        <div> 
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "20px" }}>
                            <Bar data={dataCargaInternaJogador2} options={{ ...tamanho, plugins: { title: { display: true, text: "Carga Interna Diária" } } }} />
                          </div>

                          {/* Gráfico acumulado de ACWR */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop:"40px" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo}, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "ACWR",
                                    data: gerarValoresACWRJogador2(),
                                    backgroundColor: "rgba(105, 235, 54, 0.5)",
                                    borderColor: "rgb(114, 235, 54)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "ACWR da Carga Interna por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados da Carga Interna para o jogador 2...</p>
                      )}

                      <h3 style={{ marginTop: "50px" }}>Carga Externa DT da atleta {jogador2}</h3>
                      {cargaExternaDtDataJogador2 ? (
                        <div> 
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "20px" }}>
                            <Bar data={dataCargaExternaDTJogador2} options={{ ...tamanho, plugins: { title: { display: true, text: "Carga Externa Diária com a Distância Total Percorrida" } } }} />
                          </div>

                          {/* Gráfico acumulado de ACWR */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop:"40px" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "ACWR DT",
                                    data: gerarValoresACWRdtJogador2(),
                                    backgroundColor: "rgba(105, 235, 54, 0.5)",
                                    borderColor: "rgb(114, 235, 54)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "ACWR da Distância Total Percorrida por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados da Carga Externa DT para o jogador 2...</p>
                      )}

                      <h3 style={{ marginTop: "50px" }}>Carga Externa HS da atleta {jogador2}</h3>
                      {cargaExternaHsDataJogador2 ? (
                        <div> 
                          {/* Gráfico das Médias */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop: "20px" }}>
                            <Bar data={dataCargaExternaHSJogador2} options={{ ...tamanho, plugins: { title: { display: true, text: "Carga Externa Diária com a Distância Percorrida em Alta Velocidade" } } }} />
                          </div>

                          {/* Gráfico acumulado de ACWR */}
                          <div style={{ width: "500px", height: "300px", margin: "auto", marginTop:"40px" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "ACWR HS",
                                    data: gerarValoresACWRhsJogador2(),
                                    backgroundColor: "rgba(105, 235, 54, 0.5)",
                                    borderColor: "rgb(114, 235, 54)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "ACWR da Distância Percorrida em Alta Velocidade por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados da Carga Externa HS para o jogador 2...</p>
                      )}
                    </div>
                  )}                  
                </div>
              </div>
            </div>   
          )}

          {variavel === "CMJ & SJ" && (
            <div style={{ marginTop: "30px" }}>
              <h2>CMJ & SJ</h2>

              {/* Contêiner para os dados lado a lado */}
              <div style={{ display: "flex", justifyContent: "center", gap: "100px", marginTop: "20px" }}>
                <div>
                  {/* Seleção do jogador 1 */}
                  <label style={{ fontSize: "18px", marginRight: "10px" }}>
                    Jogador 1:
                  </label>
                  <select
                    value={jogador1}
                    onChange={(e) => setJogador1(e.target.value)}
                    style={{ padding: "8px", fontSize: "16px"}}
                  >
                    <option value="">Selecione um jogador</option>
                    {jogadores.map((nome, index) => (
                      <option key={index} value={nome}>
                        {nome}
                      </option>
                    ))}
                  </select>

                  {/* Exibir a análise CMJ para o jogador 1 */}
                  {jogador1 && (
                    <div style={{ marginTop: "20px" }}>
                      <h3 style={{ marginTop: "40px" }}>CMJ & SJ da atleta {jogador1}</h3>

                      {cmjValoresJogador1 ? (
                        <div>                                          
                          {/* Gráfico acumulado de CMJ */}
                          <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "CMJ por Microciclo",
                                    data: cmjValoresJogador1,
                                    backgroundColor: "rgba(105, 235, 54, 0.5)",
                                    borderColor: "rgb(114, 235, 54)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "CMJ por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados do CMJ para o jogador 1...</p>
                      )}

                      {sjValoresJogador1 ? (
                        <div>                                          
                          {/* Gráfico acumulado de SJ */}
                          <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "SJ por Microciclo",
                                    data: sjValoresJogador1,
                                    backgroundColor: "rgba(241, 177, 16, 0.68)",
                                    borderColor: "rgb(255, 206, 86)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "SJ por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados do SJ para o jogador 1...</p>
                      )}                    
                    </div>
                  )}
                </div>

                <div>
                  {/* Seleção do jogador 2 */}
                  <label style={{ fontSize: "18px", marginRight: "10px" }}>
                    Jogador 2:
                  </label>
                  <select
                    value={jogador2}
                    onChange={(e) => setJogador2(e.target.value)}
                    style={{ padding: "8px", fontSize: "16px"}}
                  >
                    <option value="">Selecione um jogador</option>
                    {jogadores.map((nome, index) => (
                      <option key={index} value={nome}>
                        {nome}
                      </option>
                    ))}
                  </select>

                  {/* Exibir a análise CMJ para o jogador 2 */}
                  {jogador2 && (
                    <div style={{ marginTop: "20px" }}>
                      <h3 style={{ marginTop: "40px" }}>CMJ & SJ da atleta {jogador2}</h3>

                      {cmjValoresJogador2 ? (
                        <div>                                          
                          {/* Gráfico acumulado de CMJ */}
                          <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "CMJ por Microciclo",
                                    data: cmjValoresJogador2,
                                    backgroundColor: "rgba(105, 235, 54, 0.5)",
                                    borderColor: "rgb(114, 235, 54)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "CMJ por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados do CMJ para o jogador 1...</p>
                      )}

                      {sjValoresJogador2 ? (
                        <div>                                          
                          {/* Gráfico acumulado de SJ */}
                          <div style={{ width: "500px", height: "300px", margin: "auto" }}>
                            <Bar 
                              data={{
                                labels: Array.from({ length: microciclo }, (_, i) => `Microciclo ${i + 1}`), // Rótulos dinâmicos
                                datasets: [
                                  {
                                    label: "SJ por Microciclo",
                                    data: sjValoresJogador2,
                                    backgroundColor: "rgba(241, 177, 16, 0.68)",
                                    borderColor: "rgb(255, 206, 86)",
                                    borderWidth: 1
                                  }
                                ]
                              }}
                              options={{
                                ...tamanho,
                                plugins: { title: { display: true, text: "SJ por Microciclo" } }
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <p>A carregar os dados do SJ para o jogador 2...</p>
                      )}                    
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;


