import { Layout, Space, Typography } from "antd"
import { LoginOutlined, TeamOutlined, UserOutlined } from "@ant-design/icons"
import { CustomButton } from "../custom-button"
import { Link, useNavigate } from "react-router-dom"
import { Paths } from "../../paths"
import styles from "./index.module.css"
import { useDispatch, useSelector } from "react-redux"
import { logout, selectUser } from "../../features/auth/authSlice"


export const Header = () => {
  const user = useSelector(selectUser);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const onLogoutClick = () => {
    dispatch(logout());
    localStorage.removeItem("token");
    navigate('/login')
  }

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
      {
        user ? (
          <CustomButton type='primary' icon={<LoginOutlined />} onClick={onLogoutClick}>
            Log Out
          </CustomButton>
        ) :
          <Space>
            <Link to={Paths.register} >
              <CustomButton type="primary" icon={<UserOutlined />}>
                Sign in
              </CustomButton>
            </Link>
            <Link to={Paths.login} >
              <CustomButton type="primary" icon={<LoginOutlined />} >
                Log in
              </CustomButton>
            </Link>
          </Space>
      }
    </Layout.Header>
  )
}
