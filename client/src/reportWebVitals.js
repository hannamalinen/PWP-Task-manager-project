/**
 * This file defines the `reportWebVitals` function, which is used to measure and report web performance metrics.
 * It leverages the `web-vitals` library to collect metrics such as CLS, FID, FCP, LCP, and TTFB.
 */

const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;
