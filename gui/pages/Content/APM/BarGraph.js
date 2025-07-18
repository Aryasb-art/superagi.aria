import React, {useEffect, useRef, useState} from "react";

export const BarGraph = ({data, type, color}) => {
  const chartRef = useRef(null);
  const containerRef = useRef(null);
  const [echartsLoaded, setEchartsLoaded] = useState(false);
  const [chartInstance, setChartInstance] = useState(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Dynamic import of echarts only on client side
    import('echarts').then((echarts) => {
      setEchartsLoaded(true);
      
      if (!chartRef.current) return;

      const existingInstance = echarts.getInstanceByDom(chartRef.current);
      const chart = existingInstance ? existingInstance : echarts.init(chartRef.current);
      setChartInstance(chart);

      const option = {
        color: color,
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: data.map(item => item.name),
          axisLabel: {
            interval: 0,
            rotate: 45,
            color: '#888'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: function (value) {
              if (value >= 1000) {
                return `${value / 1000}k`;
              } else {
                return value;
              }
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.08)'
            }
          }
        },
        series: [{
          data: data.map(item => type === 'tokens_per_call' ? (item.tokens_consumed / item.calls) : item[type]),
          type: 'bar'
        }],
        responsive: true
      };

      chart.setOption(option);

      // Only use ResizeObserver on client side
      if (typeof ResizeObserver !== 'undefined' && containerRef.current) {
        const resizeObserver = new ResizeObserver(entries => {
          entries.forEach(entry => {
            chart.resize();
          });
        });

        resizeObserver.observe(containerRef.current);

        return () => {
          resizeObserver.disconnect();
        };
      }
    }).catch(error => {
      console.error('Failed to load echarts:', error);
    });
  }, [data, type, color]);

  useEffect(() => {
    return () => {
      if (chartInstance && typeof window !== 'undefined') {
        chartInstance.dispose();
      }
    };
  }, [chartInstance]);

  // Show loading state during SSR or while echarts is loading
  if (typeof window === 'undefined' || !echartsLoaded) {
    return (
      <div style={{width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div>Loading chart...</div>
      </div>
    );
  }

  return (
    <div ref={containerRef} style={{width: '100%', height: '100%'}}>
      <div ref={chartRef} style={{width: '100%', height: '100%'}}></div>
    </div>
  );
}

export default BarGraph;