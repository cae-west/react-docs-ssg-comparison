import React from 'react';
import Layout from '@theme/Layout';
import {HomeContent} from '../react-home/components/Layout/HomeContent';
import '../css/react-home.css';

export default function Home() {
  return (
    <Layout title="React" description="The library for web and native user interfaces" wrapperClassName="rd-home">
      <HomeContent />
    </Layout>
  );
}
