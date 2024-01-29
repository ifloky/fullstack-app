import React from 'react';
import { Layout as antLayout } from 'antd';
import styles from './index.module.css'
import { Header } from '../header';

type Props = {
  children: React.ReactNode
}

export const Layout = ({ children }: Props) => {
  return (
    <div className={styles.main}>
      <Header />
      <antLayout.Content style={{ height: '100%' }}>
        {children}
      </antLayout.Content>
    </div>
  )
}
