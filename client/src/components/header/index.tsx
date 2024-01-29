import { Layout, Space, Typography } from "antd"
import { LoginOutlined, TeamOutlined, UserOutlined } from "@ant-design/icons"
import { CustomButton } from "../custom-button"
import { Link } from "react-router-dom"
import { Paths } from "../../paths"
import styles from "./index.module.css"


export const Header = () => {
  return (
    <Layout.Header className={styles.header}>
      <Space align="center">
        <TeamOutlined className={styles.teamIcon} />
        <Link to={Paths.home} >
          <CustomButton type="link">
            <Typography.Paragraph> Employee</Typography.Paragraph>
          </CustomButton>
        </Link>
      </Space>
      <Space>
        <Link to={Paths.register} >
          <CustomButton type="link" icon={<UserOutlined />}>
            Sign in
          </CustomButton>
        </Link>
        <Link to={Paths.login} >
          <CustomButton type="link" icon={<LoginOutlined />} >
            Log in
          </CustomButton>
        </Link>
      </Space>
    </Layout.Header>
  )
}
