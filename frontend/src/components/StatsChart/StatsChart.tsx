import { Chart, ChartConfiguration, ChartItem } from 'chart.js'
import { onCleanup, onMount, createSignal } from 'solid-js'

import { socket, data } from '../../runtimeData'

import classes from './StatsChart.module.scss'

const chartSettings: ChartConfiguration = {
    type: 'doughnut',
    data: {
        labels: ['Used', 'Free'],
        datasets: [{
            data: [50, 50],
            backgroundColor: ['#febd67', '#ffe9cc'],  // Used, Free
            hoverOffset: 5,
        }]
    },
    options: {
        plugins: {
            title: {
                display: true,
                color: '#000',
                font: {
                    size: 16,
                    weight: '500'
                }
            },
            legend: {
                display: false
            }
        }
    },
}

export default function Graph({id, label}: {id: string, label: string}) {
    var self: Chart
    const [dataLabel, setLabel] = createSignal<string>('0')
    const chartID = `chart-${id}`
    const base = id === 'cpu'  ? 100 : 512
    const measurmentUnit = id === 'cpu'  ? '%' : 'MB'

    const settings: ChartConfiguration = {
        ...chartSettings,
        options: {
            plugins: {
                ...chartSettings.options.plugins,
                title: {
                    ...chartSettings.options.plugins.title,
                    text: label
                },
                tooltip: {
                    callbacks: {
                        label: (item) => `${item.parsed}${measurmentUnit} ${item.label}`
                    }
                }
            }
        },
    }

    function updateData() {
        data; const used = eval(`data.overview.vars.${id}_used`)
        
        self.data.datasets[0].data = [used, base - used]
        self.update()

        setLabel(Math.round(used / base * 100).toString())
    }

    onMount(() => {
        self = new Chart(
            (document.getElementById(chartID) as HTMLCanvasElement)?.getContext('2d') as ChartItem, 
            settings
        )
        updateData()

        socket.on('data_changed', updateData)
    })

    onCleanup(() => {
        socket.off('data_changed', updateData)
    })
    
    return (
        <div class={classes.Stats}>
            <div class={classes.Label}>{dataLabel() + '%'}</div>
            <canvas id={chartID}/>
        </div>
    )
}
