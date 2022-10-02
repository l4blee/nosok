import { Chart, ChartConfiguration, ChartItem } from 'chart.js'
import { onCleanup, onMount, createSignal } from 'solid-js'

import { refreshData, socket, data } from '../../runtimeData'

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

export default function Graph({id, label, area}: {id: string, label: string, area: string}) {
    var self: Chart
    const [dataLabel, setLabel] = createSignal<string>('0')
    const chartID = `chart-${id}`

    const settings: ChartConfiguration = {
        ...chartSettings,
        options: {
            plugins: {
                title: {
                    ...chartSettings.options.plugins.title,
                    text: label
                }
            }
        }
    }

    function updateData() {
        const base = id === 'cpu'  ? 100 : 512
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

        refreshData().then(updateData)

        socket.on('data_changed', updateData)
    })

    onCleanup(() => {
        socket.off('data_changed', updateData)
    })
    
    return (
        <div class={classes.Stats}>
            <div class={classes.Label}>{dataLabel() + '%'}</div>
            <canvas id={chartID} style={`grid-area: ${area}`}/>
        </div>
    )
}
