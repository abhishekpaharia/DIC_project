import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js';
import './App.css';

function App() {
  const [plot1, setPlot1] = useState("")
  const [plot2, setPlot2] = useState("")
  const [countries, setCountries] = useState([])
  const [selectedCountryIndex, setSelectedCountryIndex] = useState(-1)

  //common
  const [Adult_Mortality, setAdult_Mortality] = useState('')
  const [Income_resources, setIncome_resources] = useState('')
  const [Schooling, setSchooling] = useState('')

  //developing
  const [HIV_AIDS, setHIV_AIDS] = useState('')
  const [GDP, setGDP] = useState('')
  const [five_deaths, setfive_deaths] = useState('')

  //developed
  const [percentage_expenditure, setpercentage_expenditure] = useState('')
  const [thinness_1_19_years, setthinness_1_19_years] = useState('')
  const [thinness_5_9_years, setthinness_5_9_years] = useState('')

  const [isPlotShown, setIsPlotShown] = useState(false)

  // this function is called when predict button is clicked. 
  //it will call predict api endpoint and sends user input in request and get plot data in response
  const handleSubmit = e => {
    e.preventDefault();
    console.log("form value", e.target.value)

    let inputs = {}
    if (Adult_Mortality !== '') {
      inputs.Adult_Mortality = parseFloat(Adult_Mortality)
    }
    if (Income_resources !== '') {
      inputs.Income_resources = parseFloat(Income_resources)
    }
    if (Schooling !== '') {
      inputs.Schooling = parseFloat(Schooling)
    }

    if (countries[selectedCountryIndex].status === 'Developing') {
      if (HIV_AIDS !== '') {
        inputs.HIV_AIDS = parseFloat(HIV_AIDS)
      }
      if (GDP !== '') {
        inputs.GDP = parseFloat(GDP)
      }
      if (five_deaths !== '') {
        inputs.five_deaths = parseFloat(five_deaths)
      }
    }

    if (countries[selectedCountryIndex].status === 'Developed') {
      if (percentage_expenditure !== '') {
        inputs.percentage_expenditure = parseFloat(percentage_expenditure)
      }
      if (thinness_1_19_years !== '') {
        inputs.thinness_1_19_years = parseFloat(thinness_1_19_years)
      }
      if (thinness_5_9_years !== '') {
        inputs.thinness_5_9_years = parseFloat(thinness_5_9_years)
      }
    }

    let body = {
      "countryname": countries[selectedCountryIndex].name,
      "inputs": inputs
    }
    fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body)
    })
      .then(res => {
        res.json().then(data => {
          console.log(data)
          console.log(JSON.parse(data.fig1))
          console.log(JSON.parse(data.fig2))
          let fig1 = JSON.parse(data.fig1)
          let fig2 = JSON.parse(data.fig2)
          fig1.layout.width = 1150
          fig1.layout.height = 600
          fig2.layout.width = 1150
          fig2.layout.height = 600
          setPlot1(fig1)
          setPlot2(fig2)
          setIsPlotShown(true)
        })
        //console.log(res)
      })
  }

  //this function is called when clear button is clicked and it clears the screen
  const onClear = (e) => {
    e.preventDefault();
    setAdult_Mortality('')
    setIncome_resources('')
    setSchooling('')
    setHIV_AIDS('')
    setGDP('')
    setfive_deaths('')
    setpercentage_expenditure('')
    setthinness_1_19_years('')
    setthinness_5_9_years('')
    setIsPlotShown(false)
  }

  //fetching the list of the counties in start of app
  useEffect(() => {
    fetch('/countries').then(res => {
      res.json().then(data => {
        setCountries(data)
        console.log("countries", data)
        setSelectedCountryIndex(0)
      })
    })
  }, [])

  return (
    <div className="App">
      <h1>Life expectancy predictor</h1>
      <form>
        <div style={{width:'40%'}}>
          <label>Choose a Country:</label>
          <select required name="countries" id="countries" defaultValue={selectedCountryIndex} value={selectedCountryIndex}
            onChange={(e) => {
              console.log(e.target.value)
              setSelectedCountryIndex(e.target.value)
            }}>
            {
              countries.map((country, index) => {
                return <option key={index} value={index}>{country.name}</option>
              })
            }
          </select>
        </div>
        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'flex-start' }}>
          {selectedCountryIndex !== -1 &&
            <div style={{ padding: '20px' }}>
              <label>Adult_Mortality:</label>
              <input type='number' step={"any"} name='Adult_Mortality' id='Adult_Mortality' value={Adult_Mortality}
                onChange={e => { setAdult_Mortality(e.target.value) }}></input>

              <label>Income_resources:</label>
              <input type='number' step={"any"} name='Income_resources' id='Income_resources' value={Income_resources}
                onChange={e => setIncome_resources(e.target.value)}></input>

              <label>Schooling:</label>
              <input type='number' step={"any"} name='Schooling' id='Schooling' value={Schooling}
                onChange={e => setSchooling(e.target.value)}></input>
            </div>
          }

          {selectedCountryIndex !== -1 && countries[selectedCountryIndex].status === 'Developing' &&
            <div style={{ padding: '20px' }}>
              <label>HIV_AIDS:</label>
              <input type='number' step={"any"} name='HIV_AIDS' id='HIV_AIDS' value={HIV_AIDS}
                onChange={e => { setHIV_AIDS(e.target.value) }}></input>

              <label>GDP:</label>
              <input type='number' step={"any"} name='GDP' id='GDP' value={GDP}
                onChange={e => setGDP(e.target.value)}></input>

              <label>under-five_deaths:</label>
              <input type='number' step={"any"} name='five_deaths' id='five_deaths' value={five_deaths}
                onChange={e => setfive_deaths(e.target.value)}></input>

            </div>

          }

          {selectedCountryIndex !== -1 && countries[selectedCountryIndex].status === 'Developed' &&
            <div style={{ padding: '20px' }}>
              <label>percentage_expenditure:</label>
              <input type='number' step={"any"} name='percentage_expenditure' id='percentage_expenditure' value={percentage_expenditure}
                onChange={e => { setpercentage_expenditure(e.target.value) }}></input>

              <label>thinness_1_19_years:</label>
              <input type='number' step={"any"} name='thinness_1_19_years' id='thinness_1_19_years' value={thinness_1_19_years}
                onChange={e => setthinness_1_19_years(e.target.value)}></input>

              <label>thinness_5_9_years:</label>
              <input type='number' step={"any"} name='thinness_5_9_years' id='thinness_5_9_years' value={thinness_5_9_years}
                onChange={e => setthinness_5_9_years(e.target.value)}></input>
            </div>}
        </div>
        <button onClick={handleSubmit}>predict</button>
        <button onClick={onClear}> clear </button>
      </form>
      {isPlotShown &&
        <div>
          <Plot data={plot1.data} layout={plot1.layout} />
          <Plot data={plot2.data} layout={plot2.layout} />
        </div>
      }
    </div >
  );
}

export default App;
