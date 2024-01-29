import { Row, Card, Form, Space, Typography } from 'antd'
import { Layout } from '../../components/layout'
import { CustomInput } from '../../components/custom-input'
import { PasswordInput } from '../../components/password-input'
import { CustomButton } from '../../components/custom-button'
import { Link } from 'react-router-dom'
import { Paths } from '../../paths'

export const Login = () => {
  return (
    <Layout>
      <Row align="middle" justify="center">
        <Card title="Log in" style={{ width: "30rem" }}>
          <Form onFinish={() => null}>
            <CustomInput name={'email'} placeholder={'Enter your email'} type="email"></CustomInput>
            <PasswordInput name={'password'} placeholder={'Enter your password'}></PasswordInput>
            <CustomButton type="primary" htmlType='submit'>Log in</CustomButton>
          </Form>
          <Space direction='vertical' size='large'>
            <Typography.Text>
              No account? <Link to={Paths.register}>Sign in</Link>
            </Typography.Text>
          </Space>
        </Card>
      </Row>
    </Layout>
  )
}
