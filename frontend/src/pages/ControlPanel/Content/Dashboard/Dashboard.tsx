import { onCleanup, onMount } from 'solid-js'

import { Chart, ChartConfiguration, ChartItem, registerables } from 'chart.js'
Chart.register(...registerables)
Chart.defaults.font = {
    family: 'Montserrat',
    size: 14
}

import classes from './Dashboard.module.scss'

import {socket, data, refreshData} from '../../../../runtimeData'


export default function Dashboard() {
    const chartSettings: ChartConfiguration = {
        type: 'line',
        data: {
            labels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            datasets: [{
                label: 'Memory usage, %',
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.3,
                pointRadius: 1,
                hitRadius: 10,
                data: [],
            },
            {
                label: 'CPU utilization, %',
                backgroundColor: 'rgb(0, 99, 132)',
                borderColor: 'rgb(0, 99, 132)',
                tension: 0.3,
                pointRadius: 1,
                hitRadius: 10,
                data: [],
            }]
        },
        options: {
            devicePixelRatio: 1.5,
            layout: {
                padding: 15
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Runtime stats',
                    color: '#000',
                    font: {
                        size: 16,
                        weight: '500'
                    }
                },
                tooltip: {
                    titleFont: {
                        size: 0
                    }
                 }
            },
            interaction: {
                intersect: false,
                mode: 'index',
            },
            scales: {
                x: {
                    ticks: {
                        display: false
                    }
                },
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            },
            responsive: false,
        },
    }

    function updateChart() {
        console.log('chart updated');
        
        const chart = Chart.getChart((document.getElementById('chart') as HTMLCanvasElement)?.getContext('2d')!)!
        chart.data.datasets[0].data = data.overview.vars.map(x => Number((x.memory_used / 512 * 100).toFixed(1)))
        chart.data.datasets[1].data = data.overview.vars.map(x => x.cpu_used)

        chart.update()
    }

    onMount(() => {
        refreshData().then(() => {
            new Chart(
                (document.getElementById('chart') as HTMLCanvasElement)?.getContext('2d') as ChartItem, 
                chartSettings
            )

            updateChart()
        })

        socket.on('data_changed', updateChart)
    })

    onCleanup(() => {
        socket.off('data_changed', updateChart)
    })

    return (
        <div>
            <canvas class={classes.Stats} id='chart' aria-label='Stats' role='img' style='grid-area: runtime'/>
        </div>
    )
}