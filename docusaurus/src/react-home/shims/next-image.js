// Stand-in for next/image.
import React from 'react';
import useBaseUrl from '@docusaurus/useBaseUrl';
export default function Image({src, alt = '', width, height, priority, quality, placeholder, blurDataURL, fill, loader, unoptimized, sizes, style, ...rest}) {
  const url = useBaseUrl(typeof src === 'string' ? src : src && src.src);
  const fillStyle = fill ? {position: 'absolute', inset: 0, width: '100%', height: '100%'} : {};
  return <img src={url} alt={alt} width={fill ? undefined : width} height={fill ? undefined : height} style={{...fillStyle, ...style}} {...rest} />;
}
